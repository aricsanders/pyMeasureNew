#-----------------------------------------------------------------------------
# Name:        AbstractDjangoModels.py
# Purpose:    To serve as a storage location for important Django Models
# Author:      Aric Sanders
# Created:     3/21/2016
# License:     MIT License
#-----------------------------------------------------------------------------
""" Abstract Django models is a module that stores django models that can be inherited from.
The models can also be cut and pasted"""
#-----------------------------------------------------------------------------
# Standard Imports
import datetime
#-----------------------------------------------------------------------------
# Third Party Imports
from django.db import models
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User,Group
from django.contrib.auth import get_user_model
#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions
def user_directory_path(instance, filename):
    """Helper function for saving user files. Structure is MEDIA_ROOT/username/year/month/filename"""
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    today=datetime.date.today()
    return '{0}/{1}/{2:0>2d}/{3}'.format(instance.owner.get_username(), today.year,today.month,filename)
#-----------------------------------------------------------------------------
# Module Classes
class UploadUserFile(models.Model):
    """Container to upload a file and track users"""
    owner=models.ForeignKey(User)
    file = models.FileField(upload_to=user_directory_path)
    class Meta:
        abstract=True

class UserFile(models.Model):
    """Container that acts as a closed entity reference for the website"""
    owner=models.ForeignKey(settings.AUTH_USER_MODEL)
    location=models.CharField('Location on Disk', max_length=200) # Could use URL Field, but it is essentially just this
    url=models.CharField('URL of the file', max_length=200)
    name=models.CharField('Name of the resource', max_length=200)
    class Meta:
        abstract=True
    def __str__(self):
        return self.name


class Project(models.Model):
    """Container for Projects that provides structure to a collection
    of data files"""
    name=models.CharField('Name of the Project', max_length=200)
    groups=models.ManytoMany(Group)
    type=models.ForeignKey(ProjectTypes)
    description=models.TextField("A description of the project")
    wall=models.TextField("A log of comments and such for the project")

#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    pass
    