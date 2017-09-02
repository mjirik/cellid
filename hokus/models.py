from django.db import models

# Create your models here.

from django.db import models
import filer
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField

class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = FilerImageField(null=True, blank=True,
                           related_name="logo_company")
    disclaimer = FilerFileField(null=True, blank=True,
                                related_name="disclaimer_company")