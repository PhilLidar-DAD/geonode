import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

import csv

from geonode.cephgeo.models import FTPRequest, UserJurisdiction
from geonode.datarequests.models import DataRequestProfile

import geonode.settings as settings

import django

django.setup()

from pprint import pprint

def main():
    users = []
    for fr in FTPRequest.objects.all():
        users.append(fr.user)

    jurisdictions = []
    for u in users:
        try:
            j = UserJurisdiction.objects.get(user=u)
            jurisdictions.append(j)
        except Exception:
            pprint("skipping user...")

    requests  = []
    
    for j in jurisdictions:
        try:
            r = DataRequestProfile.objects.get(profile=j.user, jurisdiction_shapefile = j.jurisdiction_shapefile)
            requests.append(r)
        except Exception:

            pprint("skipping...")
        

    file_out = "place_name.csv"
    with open(file_out, "wb") as csvfile:
        csv_writer = csv.writer(csvfile)
        for r in requests:
            csv_writer.writerow([r.profile.username, r.jurisdiction_shapefile.typename, r.place_name])
        
if __name__ == '__main__':
    main()

