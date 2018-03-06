import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")


import csv
from geonode.cephgeo.models import FTPRequest, UserJurisdiction
from geonode.datarequests.models import DataRequestProfile
import geonode.settings as settings

from geonode.tasks.ftp import process_ftp_request
from geonode.cephgeo.models import CephDataObject, FTPRequest, FTPStatus, FTPRequestToObjectIndex, UserTiles, DataClassification
import datetime
from django.db.models import Q

def main(daysbefore=180):
    today_min = datetime.datetime.combine(datetime.date.today()-datetime.timedelta(days=180), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

    pending_list = FTPRequest.objects.filter(date_time__range=(today_min, today_max)).filter(Q(status=1)|Q(status=2))
    print pending_list
    for ftp_request in pending_list:
        obj_name_dict = dict()
        obj_index = FTPRequestToObjectIndex.objects.filter(ftprequest=ftp_request)
        for eachobj in obj_index:
            obj = eachobj.cephobject
            if DataClassification.labels[obj.data_class] in obj_name_dict:
                obj_name_dict[DataClassification.labels[obj.data_class].encode('utf8')].append(obj.name.encode('utf8'))
            else:
                obj_name_dict[DataClassification.labels[obj.data_class].encode('utf8')] = [obj.name.encode('utf8'), ]
        ##todo; delete empty folder
        process_ftp_request(ftp_request, obj_name_dict)

if __name__ == '__main__':
    main()


