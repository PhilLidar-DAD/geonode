import csv
import datetime
from pprint import pprint

from geonode.settings import GEONODE_APPS
from geonode.datarequests.utils import get_area_coverage
from geonode.eula.models import AnonDownloader
import geonode.settings as settings
import os, sys
from actstream.models import Action



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

def get_layer_size():
    auth_dl = Action.objects.filter(verb='downloaded').order_by('timestamp')
    results = []
    done = ["philgrid"]
    pprint("processing authenticated downloaded layers")
    for action in auth_dl:
        if action.action_object.name not in done:
            area =  get_area_coverage("\""+action.action_object.name+"\"")
            results.append([action.action_object.typename, area])
            done.append(action.action_object.name) 
        #break
    pprint("done with authenticated downloaded layers")

    pprint("processing anonymous downloads")
    anon_dl = AnonDownloader.objects.all().order_by('date')
    for item in anon_dl:
        if item.anon_layer.name not in done:
            area = get_area_coverage("\""+item.anon_layer.name+"\"")
            results.append([item.anon_layer.typename, area])
            done.append(item.anon_layer.name)
        #break
    pprint("done with anonymous downloads")

    return results


def write_to_csv(file_name, result):
    with open(file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Layer Name', 'Area in Sq. Km.']) 
        for i in result:
            writer.writerow(i)   


def main(argv):
    write_to_csv("downloads_layer_area.csv", get_layer_size())

if __name__ == "__main__":
    main(sys.argv[1:])
