# -*- coding: utf-8 -*-
#!/usr/bin/python

# Setup GeoNode environment
import os
import sys
from pprint import pprint
# from os.path import abspath, dirname, join
# PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
# sys.path.append(join(PROJECT_ROOT, 'geonode'))
# sys.path.append(PROJECT_ROOT)

from geonode.settings import GEONODE_APPS
import geonode.settings as settings
from django.contrib.auth.models import Group
from geonode.people.models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from geonode.documents.models import Document
from geonode.base.models import ResourceBase
from guardian.shortcuts import assign_perm, get_anonymous_user
import psycopg2
import psycopg2.extras
from geonode.base.models import TopicCategory

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


if __name__ == "__main__":
    input_directory = "/mnt/pmsat-nas_geostorage/DAD/Working/Jok/lipad_docs"
    path, dirs, files = os.walk(input_directory).next()
    file_count = len(files)
    print "Total number of docs: ", file_count
    ctr = 1

    for doc_file in os.listdir(input_directory):

        print '#' * 40

        print "Uploading ", str(ctr), " of ", file_count, ":", doc_file

        t = open(os.path.join(input_directory,doc_file), 'r')
        f = SimpleUploadedFile(doc_file, t.read(), 'application/pdf')
        superuser = Profile.objects.get(id=1)
        doc_title = doc_file.replace('.pdf','').replace('_',' ')
        c = Document.objects.create(
        doc_file=f,
        owner=superuser,
        title=doc_title,
        doc_type='presentation')

        print c, ': Updating doc permissions...'
        anon_group = Group.objects.get(name='anonymous')
        assign_perm('view_resourcebase', anon_group, c.get_self_resource())
        assign_perm('view_resourcebase', get_anonymous_user(), c.get_self_resource())
        assign_perm('download_resourcebase', anon_group, c.get_self_resource())
        assign_perm('download_resourcebase', get_anonymous_user(), c.get_self_resource())
        ctr+=1

    print "Finished"

