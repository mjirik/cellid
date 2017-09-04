from django.db import models

# Create your models here.

from django.db import models
import filer
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField
from django.contrib.auth.models import User
from django.db.models.signals import post_save

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


class ImageQuatro(models.Model):
    description = models.CharField(max_length=255, blank=True)
    multicell_dapi = models.FileField(upload_to='documents/')
    multicell_fitc = models.FileField(upload_to='documents/')
    singlecell_dapi = models.FileField(upload_to='documents/')
    singlecell_fitc = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)