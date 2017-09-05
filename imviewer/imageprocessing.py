# author Jan Malek and Miroslav Jirik

import os
import os.path as op
import matplotlib.pyplot as plt

import numpy as np
import skimage
import skimage.filters
import skimage.measure
from skimage import morphology
from skimage.color import label2rgb
from skimage import io
import scipy.misc as scm
from scipy import ndimage
import os.path as op

import io3d
#import imtools
#import imtools.qmisc
#import cv2 as cv

def handle_uploaded_file(files):
    pass


p1 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\sw620_stack1_w1sc-DAPI_s3.stk.tif"
p2 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\sw620_stack1_w2sc-FITC_s3.stk.tif"
p3 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\k_nalezeni\\91_w1sc-DAPI.stk.tif"
p4 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\k_nalezeni\\91_w2sc-FITC.stk.tif"
p5 = "C:\\Users\\Jan\\Desktop\\bunkoteckyVystup_3_9"
#p1 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\sw620_stack1_w1sc-DAPI_s3.stk.tif"
#p2 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\sw620_stack1_w2sc-FITC_s3.stk.tif"
#p3 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\k_nalezeni\\71_w1sc-DAPI.stk.tif"
#p4 = "C:\\Users\\Jan\\Desktop\\bunkotecky\\k_nalezeni\\71_w2sc-FITC.stk.tif"
#p5 = "C:\\Users\\Jan\\Desktop\\bunkoteckyVystup_sw620_stack1_s3_7"


def quatrofile_processing(multicell_dapi, multicell_fitc, singlecell_dapi, singlecell_fitc, outputpath):
    outPath = outputpath
    makeDirTree(outPath)

    allDapi3D = load3DData(multicell_dapi)
    allFict3D = load3DData(multicell_fitc)
    allDapiFlat = flatten(allDapi3D)
    allFitcFlat = flatten(allFict3D)
    allDapiTreshold = treshold(allDapiFlat, 180)
    allLabels, allNumObjects = label(allDapiTreshold)
    allBBoxList = getBBoxList(allLabels)

    allFusion = imageFusion(allDapiFlat, allFitcFlat)
    allFusionLabels = printLabelsOnImage(allBBoxList, allFusion, allNumObjects)
    scm.imsave(op.join(outPath, 'Popisky.png'), allFusionLabels)

    allSplitMasksList = splitMasks(allLabels, allBBoxList, allNumObjects)
    allSplitFusionList = splitObjects(allFusion, allBBoxList, allNumObjects)

    bDapi3D = load3DData(singlecell_dapi)
    bFict3D = load3DData(singlecell_fitc)
    bDapi3DFiltered = horizontalFilter(bDapi3D)
    bDapiFlat = flatten(bDapi3DFiltered)
    bFitcFlat = flatten(bFict3D)
    bDapiTreshold = treshold(bDapiFlat, 10)
    bLabels, bNumObjects = label(bDapiTreshold)
    bBBoxList = getBBoxList(bLabels)
    bLargestObjectIndex = getLargestObjectIndex(bBBoxList)
    bBBox = bBBoxList[bLargestObjectIndex]
    bFusion = imageFusion(crop(bDapiFlat, bBBox), crop(bFitcFlat, bBBox))
    scm.imsave(op.join(outPath, 'hledana.png'), bFusion)

    bSplitMasksList = splitMasks(bLabels, bBBoxList, bNumObjects)
    bMask = bSplitMasksList[bLargestObjectIndex]
    allMaskedFlatFitcList = maskMultiple(allFitcFlat, allSplitMasksList, allBBoxList, allNumObjects)
    bMaskedFlatFitc = mask(crop(bFitcFlat, bBBox), bMask)
    bCharasteristics = getObjectCharacteristics(bMask, bMaskedFlatFitc)
    allObjectsCharacteristicsTable = getAllObjectsCharacteristics(allSplitMasksList, allMaskedFlatFitcList,
                                                                  allNumObjects)

    bIsRound = (bCharasteristics[0] < 1.3) and (bCharasteristics[1] < 2000)
    orderedObjects = orderBasedOnCharacteristics(allSplitFusionList, allObjectsCharacteristicsTable, bCharasteristics,
                                                 bIsRound, allNumObjects)
    for i in range(0, allNumObjects):
        scm.imsave(op.join(outPath, 'serazeno',  str(i) + '_' + str(orderedObjects[i, 1]) + '.png'), orderedObjects[i, 0])


def makeDirTree(path):
    if not os.path.exists(op.join(path, 'serazeno')):
        if not os.path.exists(path):
            os.makedirs(path)
        os.makedirs(op.join(path, '\\serazeno'))


def load3DData(path):
    return io3d.read(path)[0]


def flatten(image3D):
    N, w, h = image3D.shape
    maxIm = np.zeros((w, h), np.float)
    for i in range(1, (image3D.shape[0] - 10) / 12 - 1):
        averageIm = image3D[i * 12]
        for j in range(1, 12):
            averageIm += image3D[i * 12 + j]
        averageIm /= 12
        maxIm = np.maximum(maxIm, averageIm).astype(np.int)
    return maxIm


def treshold(image3D, tresholdValue):
    tres = image3D > tresholdValue
    kernel = skimage.morphology.diamond(3).astype(np.uint8)
    closing = ndimage.binary_closing(tres, structure=kernel)
    return ndimage.binary_opening(closing, structure=kernel)


def label(imageTreshold):
    return ndimage.label(imageTreshold)


def getBBoxList(labeledImage):
    return ndimage.find_objects(labeledImage)


def p_imadj(image):
    mx = np.max(image)
    mn = np.min(image)
    b = 250.0 / (mx - mn)
    return ((image - mn) * b).astype(np.uint8)


def imageFusion(imageDapi, imageFitc):
    imageDapi_adj = p_imadj(imageDapi)
    imageFitc_adj = p_imadj(imageFitc)
    fusion = np.zeros([imageDapi.shape[0], imageDapi.shape[1], 3], dtype=np.uint8)
    fusion[:, :, 0] = imageDapi_adj
    fusion[:, :, 1] = imageFitc_adj
    return fusion


def printLabelsOnImage(bBoxes, image, numObjects):
    import cv2 as cv
    labeledImage = np.array(image)

    for i in range(0, numObjects):
        upLimit = int(bBoxes[i][0].start)
        if upLimit < 50: upLimit = 50
        rightLimit = int(bBoxes[i][1].stop)
        if rightLimit > labeledImage.shape[1] - 120: rightLimit = labeledImage.shape[1] - 120
        labeledImage = cv.putText(labeledImage, str(i), (rightLimit + 2, upLimit - 2), cv.FONT_HERSHEY_SIMPLEX, 2,
                                  color=(255, 255, 255))
        labeledImage = cv.rectangle(labeledImage, (int(bBoxes[i][1].start), int(bBoxes[i][0].start)),
                                    (int(bBoxes[i][1].stop), int(bBoxes[i][0].stop)), color=(255, 255, 255))
    return labeledImage


def crop(image, bBox):
    return image[bBox[0].start:bBox[0].stop, bBox[1].start:bBox[1].stop].astype(int)


def splitMasks(labels, bBoxList, numObjects):
    singleMask = [None] * numObjects
    for i in range(0, numObjects):
        singleLabel = crop(labels, bBoxList[i])
        singleMask[i] = (singleLabel == i + 1).astype(int)
    return singleMask


def splitObjects(image, bBoxList, numObjects):
    singleObjectsList = [None] * (numObjects)
    for i in range(0, numObjects):
        singleObjectsList[i] = crop(image, bBoxList[i])
    return singleObjectsList


def mask(image, mask):
    return image * mask


def maskMultiple(allFitcFlat, allSplitMasksList, allBBoxList, numObjects):
    allFitcFlatList = splitObjects(allFitcFlat, allBBoxList, numObjects)
    allFitcFlatMaskedList = [None] * (numObjects)
    for i in range(0, numObjects):
        allFitcFlatMaskedList[i] = mask(allFitcFlatList[i], allSplitMasksList[i])
    return allFitcFlatMaskedList


# Charakteristiky:
# 1. Poměr dlouhé a krátké osy
# 2. Plocha objektu
def getObjectCharacteristics(mask, maskedFlatFitcObject):
    dlouhaList = [None] * 360
    kratkaList = [None] * 360
    for alpha20 in range(0, 17):
        rot = ndimage.interpolation.rotate(mask, alpha20 * 20)
        rotLabel, tmp = ndimage.label(rot)
        rotBBox = ndimage.find_objects(rotLabel)
        dlouhaList[alpha20 * 20] = rotBBox[0][0].stop - rotBBox[0][0].start
        kratkaList[alpha20 * 20] = rotBBox[0][1].stop - rotBBox[0][1].start
    for alpha in range(np.argmax(dlouhaList) - 10, np.argmax(dlouhaList) + 10):
        rot = ndimage.interpolation.rotate(mask, alpha)
        rotLabel, tmp = ndimage.label(rot)
        rotBBox = ndimage.find_objects(rotLabel)
        dlouhaList[alpha] = rotBBox[0][0].stop - rotBBox[0][0].start
        kratkaList[alpha] = rotBBox[0][1].stop - rotBBox[0][1].start
    maxAlpha = np.argmax(dlouhaList)
    return dlouhaList[maxAlpha] * 1.0 / kratkaList[maxAlpha], np.count_nonzero(mask) * 1.0, getFitcCharacteristic(
        maskedFlatFitcObject) * 1.0


def getAllObjectsCharacteristics(allSplitMasksList, allMaskedFlatFitcObjectsList, numObjects):
    allObjectsCharacteristics = np.array([[None for x in range(3)] for y in range(numObjects)])
    for i in range(0, numObjects):
        allObjectsCharacteristics[i] = getObjectCharacteristics(allSplitMasksList[i], allMaskedFlatFitcObjectsList[i])
    return allObjectsCharacteristics


def getFitcCharacteristic(maskedFlatFitcObject):
    fitcMin = np.min(maskedFlatFitcObject[np.nonzero(maskedFlatFitcObject)])
    fitcMax = np.max(maskedFlatFitcObject)
    dotsTreshold = maskedFlatFitcObject > (fitcMin + fitcMax) / 2
    return ndimage.label(dotsTreshold)[1]


def horizontalFilter(image):
    axis = 2
    apply_ncolumns = image.shape[axis]
    profile_image = np.average(image, axis=axis).astype(np.int16)
    image_16 = image.astype(np.int16)
    for i in range(apply_ncolumns):
        image_16[:, :, i] -= profile_image
    return image_16


def getLargestObjectIndex(bBBoxList):
    argMax = 0
    areaMax = 0
    for i in range(len(bBBoxList)):
        area = (bBBoxList[i][0].stop - bBBoxList[i][0].start) * (bBBoxList[i][1].stop - bBBoxList[i][1].start)
        if (areaMax < area):
            areaMax = area
            argMax = i
    return argMax


def orderBasedOnCharacteristics(allSplitFusionList, allObjectsCharacteristicsTable, bCharasteristics, bIsRound,
                                numObjects):
    objectsComparisonList = np.array([[None for x in range(4)] for y in range(numObjects)])
    objectsComparisonList[:, 0] = allSplitFusionList
    for i in range(0, numObjects):
        objectsComparisonList[i, 1] = i
        pomerDlKr = allObjectsCharacteristicsTable[i][0] / bCharasteristics[0]
        pomerObsah = allObjectsCharacteristicsTable[i][1] / bCharasteristics[1]
        pomerTecek = allObjectsCharacteristicsTable[i][2] / bCharasteristics[2]
        if pomerDlKr < 1:
            pomerDlKr = 1 / pomerDlKr
        if pomerObsah < 1:
            pomerObsah = 1 / pomerObsah
        if pomerTecek < 1:
            pomerTecek = 1 / pomerTecek
        objectsComparisonList[i, 2] = pomerDlKr + pomerObsah + pomerTecek * bIsRound
    orderedObjects = np.array(sorted(objectsComparisonList, key=lambda x: x[2]))
    for i in range(0, numObjects):
        orderedObjects[i, 3] = i
    return orderedObjects