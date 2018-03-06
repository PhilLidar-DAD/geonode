from geonode.settings import GEONODE_APPS
import geonode.settings as settings
import os
from geonode.layers.models import Layer
from django.db.models import Q
from pprint import pprint
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

fhm_title = Layer.objects.filter(title__icontains='Flood Hazard Map')
fhm_name = Layer.objects.filter(name__icontains='_fh')
fhm_title_len =  len(fhm_title)
fhm_name_len =  len(fhm_name)
pprint('FHM count filtered by title: {0} | by name: {1}'.format(fhm_title_len,fhm_name_len))

if fhm_title_len > fhm_name_len:
    pprint('FHM list with proper title is more')
    more = fhm_title
    less = fhm_name
elif fhm_title_len < fhm_name_len:
    pprint('FHM list with proper name is more')
    more = fhm_name
    less = fhm_title

if more is not None:
    for layer in more:
        if layer not in less:
            print layer.name

# write list to file
with open('fhm_list.csv', 'w') as csv_file:
    field_names  = ['layer_name','owner/uploader']
    writer = csv.DictWriter(csv_file,fieldnames = field_names)
    writer.writeheader()
    # writer=csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONE)
    for layer in more:
        writer.writerow({'layer_name': layer.name, 'owner/uploader' : layer.owner.username})

print 'Done'
# crosscheck list in lipad-fmc database
