# -*- coding: utf-8 -*-
#!/usr/bin/python
# Geonode

__version__ = "0.1.1"

# Setup GeoNode environment
import os
import sys
from pprint import pprint
from os.path import abspath, dirname, join
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(join(PROJECT_ROOT, 'geonode'))
sys.path.append(PROJECT_ROOT)

from geonode.settings import GEONODE_APPS
import geonode.settings as settings
from django.contrib.auth.models import Group
from geonode.people.models import Profile
from geonode.settings import GEONODE_APPS
import geonode.settings as settings
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

input_directory = "/home/geonode/documents/tech_reports/VSU/"

def upload_map(map_obj):
	keyword_list = []

	# Add keywords
	keyword_list.append("LiDAR Survey")
	keyword_list.append("Flood Mapping")
	keyword_list.append("Phil-LiDAR 1")

	map_title = map_obj.replace(".pdf","")

	print map_obj, ": map title:", map_title

	t = open(input_directory + map_obj, 'r')
	f = SimpleUploadedFile(map_obj, t.read(), 'application/pdf')
	superuser = Profile.objects.get(id=1)
	c = Document.objects.create(
	doc_file=f,
	owner=superuser,
	title=map_title, doc_type='report')

	for keyword in (keyword_list):
		print map_obj, ': map keyword:', keyword
		c.keywords.add(keyword)

	print c, ': Updating map permissions...'
	anon_group = Group.objects.get(name='anonymous')
	assign_perm('view_resourcebase', anon_group, c.get_self_resource())
	assign_perm('view_resourcebase', get_anonymous_user(),
				c.get_self_resource())
	assign_perm('download_resourcebase', anon_group, c.get_self_resource())
	assign_perm('download_resourcebase', get_anonymous_user(),
				c.get_self_resource())

if __name__ == "__main__":
	path, dirs, files = os.walk(input_directory).next()
	file_count = len(files)
	print "Total number of maps: ", file_count
	ctr = 0

	for map_obj in sorted(os.listdir(input_directory)):
		ctr += 1
		print '#' * 40

		print "Uploading ", str(ctr), " of ", file_count, ":", map_obj
		upload_map(map_obj)

	print "Finished"
