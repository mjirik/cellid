from django.db import models

# Create your models here.

from django.db import models
import filer
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.urls import reverse

class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = FilerImageField(null=True, blank=True,
                           related_name="logo_company")
    disclaimer = FilerFileField(null=True, blank=True,
                                related_name="disclaimer_company")


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    description = models.CharField(max_length=100, default='')
    city = models.CharField(max_length=100, default='')
    website = models.URLField(default='')
    phone = models.IntegerField(default=0)
    image = models.ImageField(upload_to='profile_image', blank=True)


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)

def get_output_dir():
# 
    import datetime
    OUTPUT_DIRECTORY_PATH = "~/cellid_data"
    import os.path as op
    filename = op.join(op.expanduser(OUTPUT_DIRECTORY_PATH), datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f"))
#     print ("getnow")
#     print (filename)
    return filename

class ImageQuatro(models.Model):
    # from ..cellid import settings
    
    description = models.CharField(max_length=255, blank=True)
    multicell_dapi = models.FileField(upload_to='documents/')
    multicell_fitc = models.FileField(upload_to='documents/')
    singlecell_dapi = models.FileField(upload_to='documents/')
    singlecell_fitc = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    outputdir = models.CharField(max_length=255, blank=True, default=get_output_dir)
    # outputdir2  = models.FilePathField(path="/home/mjirik/", default="/home/mjirik/", recursive=True, allow_folders=True)
    # print(outputdir.path)
    # print(outputdir.default)

    def __str__(self):
        return self.description


    def get_absolute_url(self):
        """
        Returns the url to access a particular book instance.
        """
        print("models get_absolute_url()")
        print(self.id)
        return reverse('imviewer:image-detail', args=[str(self.id)])

    # def get_absolute_url(self):
    #     from django.urls import reverse
    #     return reverse('people.views.details', args=[str(self.id)])
    
