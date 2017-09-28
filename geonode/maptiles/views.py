from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils import simplejson as json
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q

from geonode.services.models import Service
from geonode.layers.models import Layer
from geonode.layers.utils import is_vector, get_bbox
from geonode.utils import resolve_object, llbbox_to_mercator
from geonode.utils import GXPLayer
from geonode.utils import GXPMap
from geonode.utils import default_map_config

from geonode.security.views import _perms_info_json
from geonode.cephgeo.models import CephDataObject, DataClassification, FTPRequest, UserJurisdiction, UserTiles, TileDataClass
from geonode.cephgeo.cart_utils import *
from geonode.maptiles.utils import *
from geonode.datarequests.models import DataRequestProfile, DataRequest
from geonode.documents.models import get_related_documents
from geonode.registration.models import Province, Municipality
from geonode.base.models import ResourceBase
from geonode.groups.models import GroupProfile

import geonode.settings as settings

from pprint import pprint
from datetime import datetime, timedelta, date, time

import logging

from geonode.cephgeo.utils import get_cart_datasize
from django.utils.text import slugify
from geonode.maptiles.models import SRS
from httplib import HTTPResponse


_PERMISSION_VIEW = _("You are not permitted to view this layer")
_PERMISSION_GENERIC = _('You do not have permissions for this layer.')
# Create your views here.

logger = logging.getLogger("geonode")

@login_required
def tiled_view(request, overlay=settings.TILED_SHAPEFILE, template="maptiles/maptiles_map.html", test_mode=False, jurisdiction=None):
    """Gives the configurations for the map in data tiles

    This function generates the layer configuration details required for the map view.
    Returns the template with the configuration details as context
    For form details and page layout, see maptiles_geoext_map.html and maptiles_map.html

    URLs:
        url(r'^/?$', views.tiled_view, name='maptiles_main'),
        url(r'^test/?$', views.tiled_view, { "overlay": settings.TILED_SHAPEFILE ,"test_mode":True} ),
        url(r'^interest=(?P<interest>[^/]*)$', views.tiled_view, {"overlay": settings.TILED_SHAPEFILE_TEST}),

    """
    context_dict = {}
    context_dict["grid"] = get_layer_config(
        request, overlay, "base.view_resourcebase", _PERMISSION_VIEW)
    legend_link = ''
    if not 'localhost' in settings.BASEURL:
        legend_link = settings.OGC_SERVER['default']['PUBLIC_LOCATION'] + \
            'wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&LAYER=geonode:philgrid&STYLE='
    else:
        legend_link = settings.SITEURL + \
            'geoserver/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&LAYER=geonode:philgrid&STYLE='
    try:
        context_dict["dtm_lgd"] = legend_link + settings.DTM_SLD
        context_dict["ortho_lgd"] = legend_link + settings.ORTHO_SLD
        context_dict["laz_lgd"] = legend_link + settings.LAZ_SLD
        context_dict["dsm_lgd"] = legend_link + settings.DSM_SLD
        context_dict["dtm_sld"] = settings.DTM_SLD
        context_dict["ortho_sld"] = settings.ORTHO_SLD
        context_dict["laz_sld"] = settings.LAZ_SLD
        context_dict["dsm_sld"] = settings.DSM_SLD
        context_dict["philgrid_sld"] = settings.PHILGRID_SLD
        context_dict["clear_sld"] = settings.CLEAR_SLD
    except Exception:
        context_dict["dtm"] = None
        context_dict["ortho"] = None
        context_dict["laz"] = None
        context_dict["dsm"] = None
        context_dict["philgrid_sld"] = None

    context_dict["geoserver_url"] = settings.OGC_SERVER['default']['PUBLIC_LOCATION']
    jurisdiction_object = None

    if jurisdiction is None:
        try:
            jurisdiction_object = UserJurisdiction.objects.get(
                user=request.user)
            jurisdiction_shapefile = jurisdiction_object.jurisdiction_shapefile
            context_dict["jurisdiction"] = get_layer_config(
                request, jurisdiction_object.jurisdiction_shapefile.typename, "base.view_resourcebase", _PERMISSION_VIEW)
            context_dict[
                "jurisdiction_name"] = jurisdiction_object.jurisdiction_shapefile.typename
            context_dict["jurisdiction_yes"] = True
        except Exception as e:
            context_dict["jurisdiction_yes"] = False
            print e

    else:
        context_dict["jurisdiction"] = get_layer_config(
            request, jurisdiction, "base.view_resourcebase", _PERMISSION_VIEW)

    context_dict["feature_municipality"] = settings.MUNICIPALITY_SHAPEFILE.split(":")[
        1]
    context_dict["feature_tiled"] = overlay.split(":")[1]
    context_dict["test_mode"] = test_mode
    context_dict["data_classes"] = DataClassification.labels.values()

    return render_to_response(template, RequestContext(request, context_dict))

def process_georefs(request):
    """Process the georefs submitted by the user, then redirect to cart

    This function handles the checking of selected tiles, <submitted_georef_list>, if they are listed in the tiles within the user's jurisdiction, <jurisdiction_georefs>.
        The intersection of the two mentioned list is stored to <georef_list>.
        The tiles within the user's jurisdiction is listed in the Cephgeo.UserTiles model as gridref_list column.
        If the user does not have a Cephgeo.UserTiles entry, this raises PermissionDenied
    Then filters data classes depending on the selected data classes, by removing unselected data classes in Q
    Then gets the filtered georef in CephDataObject.
    Then it adds it to cart using cart_utils's add_to_cart_unique, which checks if it has a duplicate, then it doesnt add it, if no duplicate, then it adds it.
    Then this also outputs a message of the status of the selected georefs; if with duplicates, empty georef, or succesful.
    Then redirects to geonode.cephgeo.views.get_cart

    Triggers:
        `georef_form` is submitted, also see maptiles_map.html and maptiles_geoext_map.html

    URLs:
        url(r'^addtocart/?$', views.process_georefs),

    """
    if request.method == "POST":
        try:
            ### Get georef list filtered with georefs computed upon approval of registration
            georef_area = request.POST['georef_area'] # Check maptiles_geoext_map.html for more details
            submitted_georef_list = filter(None, georef_area.split(","))

            ### Get the tiles inside jurisdiciton
            jurisdiction_georefs = []
            try:
                jurisdiction_georefs = str(UserTiles.objects.get(user=request.user).gridref_list)
            except ObjectDoesNotExist as e:
                pprint("No jurisdiction tiles for this user")
                raise PermissionDenied

            ### New list <georef_list> is an intersection of <submitted_georef_list> and <jurisdiction_georefs>
            georef_list = []
            outside_jurisdiction = []
            for georef in submitted_georef_list:
                if georef in jurisdiction_georefs:
                    georef_list.append(georef)
                else:
                    outside_jurisdiction.append(georef)
            pprint(georef_list)

            ### Get the requested dataclasses
            data_classes = list()
            for data_class in DataClassification.labels.values():
                if request.POST.get(slugify(data_class.decode('cp1252'))):
                    data_classes.append(data_class)

            ### Construct filter for excluding unselected data classes; this list will be removed in the query later
            dataclass_filter = DataClassification.labels.keys()
            for dataclass, label in DataClassification.labels.iteritems():
                if label in data_classes:
                    dataclass_filter.remove(dataclass)

            ### Initialize variables for counting empty georefs and duplicate objects
            count = 0
            empty_georefs = 0
            duplicates = []

            ### Process each georef in list
            for georef in georef_list:

                ### Build filter query to exclude unselected data classes
                filter_query = Q(name__startswith=georef)
                for filtered_class in dataclass_filter:
                    filter_query = filter_query & ~Q(data_class=filtered_class) # intersection of the original Q <filter_query>, and the Q that is not '~' data_class=filtered_class

                ### Execute query
                objects = CephDataObject.objects.filter(filter_query)
                pprint("objects found for georef:" + georef)

                ### Count duplicates and empty references
                count += len(objects)
                if len(objects) > 0:
                    for ceph_obj in objects:# Add each Ceph object to cart
                        try:
                            add_to_cart_unique(request, ceph_obj.id)
                            pprint("object " + ceph_obj.name + " added to cart")
                        except DuplicateCartItemException:# List each duplicate object
                            duplicates.append(ceph_obj.name)
                else:
                    empty_georefs += 1

            ### Inform user of the number of processed georefs and objects
            message_string = "Processed [{0}] georef tiles. ".format(len(georef_list))
            if len(outside_jurisdiction) > 0:
                message_string += "[{0}] georef tiles found outside of user's jurisdiction have been skipped. ".format(len(outside_jurisdiction))
            if len(duplicates) > 0:
                message_string += "[{0}] duplicate objects found in cart have been skipped. A total of [{1}] objects have been added to cart. ".format(len(duplicates), (count - len(duplicates)))
            else:
                message_string += "A total of [{0}] objects have been added to cart. ".format(count - len(duplicates))

            if empty_georefs > 0:
                messages.error(request, "ERROR: [{0}] out of selected [{1}] georef tiles have no data! A total of [{2}] objects have been added to cart. \n".format(
                    empty_georefs, len(georef_list), (count - len(duplicates))))
            else:
                messages.info(request, message_string)

            return redirect('geonode.cephgeo.views.get_cart')

        except ValidationError: # Redirect and inform if an invalid georef is encountered
            messages.error(request, "Invalid georefs list")
            return HttpResponseRedirect('/maptiles/')

    else: # Must process HTTP POST method from form
        raise Exception("HTTP method must be POST!")

@login_required
def georefs_validation(request):
    """Check if user has exceeded the limit for downloads as specified in the local settings <settings.SELECTION_LIMIT>

    This functions validates if the user's size to be added to cart <total_size> + cart's total size <cart_total_size> + FTPRequests since midnight <request_size_mn> exceeds the size limit <settings.SELECTION_LIMIT>

    Triggers:
        `georef_form` is submitted, also see maptiles_geoext_map.html

    URLs:
        url(r'^validate/?$', views.georefs_validation),

    """
    if request.method != 'POST':
        return HttpResponse(
            content='no data received from HTTP POST',
            status=405,
            mimetype='text/plain'
        )
    else:
        georefs = request.POST["georefs"]
        print("[VALIDATION]")
        pprint(request.POST)
        georefs_list = filter(None, georefs.split(","))

        ### Retrieve currect cart's total size; see cephgeo's utils.py
        cart_total_size = get_cart_datasize(request)

        ### Retrieve FTPRequests since midnight
        today_min = datetime.combine(date.today(), time.min)
        today_max = datetime.combine(date.today(), time.max)
        requests_today = FTPRequest.objects.filter(
            user=request.user, date_time__range=(today_min, today_max))
        request_size_mn = 0
        for r in requests_today:
            request_size_mn += r.size_in_bytes
        print "PREVIOUS REQUESTS:  "
        pprint(requests_today)

        ### Retrieve size of selection which will be added to the cart
        total_size = 0
        for georef in georefs_list:
            objects = CephDataObject.objects.filter(name__startswith=georef)
            for o in objects:
                total_size += o.size_in_bytes
        pprint('Total size:' + str(total_size))

        ### Proceed with error or success, see maptiles_geoext_map.html's display_message
        if total_size + cart_total_size + request_size_mn > settings.SELECTION_LIMIT:
            return HttpResponse(
                content=json.dumps({"response": False, "total_size": total_size,
                                    "cart_size": cart_total_size, "recent_requests_size": request_size_mn}),
                status=200,
                # mimetype='text/plain'
                content_type="application/json"
            )
        else:
            return HttpResponse(
                content=json.dumps(
                    {"response": True, "total_size": total_size, "cart_size": cart_total_size}),
                status=200,
                # mimetype='text/plain'
                content_type="application/json"
            )

@login_required
def province_lookup(request, province=""):
    """Function for looking up the municipalities within a province

    NOTE DOES NOT WORK, needs to migrate registration models, questionable code (check the appends)

    URLs:
        url(r'^provinces/?$', views.province_lookup),
        url(r'^provinces/(?P<province>[^/]*)$', views.province_lookup),

    """
    if province == "":
        provinces = []
        for p in Province.objects.all():
            p.append(p.province_name)

        return HttpResponse(
            content=json.dumps({"provinces": provinces}),
            status=200,
            content_type="application/json"
        )
    else:
        provinceObject = Province.objects.get(province_name=province)
        municipalities = []
        for m in Municipality.objects.filter(province__province_name="province"):
            m.append(m.municipality_name)

        return HTTPResponse(
            content=json.dumps(
                {"province": province, "municipalities": municipalities}),
            status=200,
            content_type="application/json",
        )

@login_required
def georefs_datasize(request):
    """Function for showing the data size of a georef

    Function to retrieve data size of each georef, see maptiles_geoext_map.html

    URLs:
        url(r'^datasize/?$', views.georefs_datasize),

    """
    if request.method != 'POST':
        return HttpResponse(
            content='no data received from HTTP POST',
            status=405,
            mimetype='text/plain'
        )
    else:
        georefs_clicked = request.POST["georefs_clicked"]
        total_data_size_clicked = 0

        georefs_clicked_list = filter(None, georefs_clicked.split(","))

        for eachgeoref_clicked in georefs_clicked_list:
            clicked_objects = CephDataObject.objects.filter(
                name__startswith=eachgeoref_clicked)
            for o in clicked_objects:
                total_data_size_clicked += o.size_in_bytes
        return HttpResponse(
            content=json.dumps(
                {"total_data_size_clicked": total_data_size_clicked}),
            status=200,
            content_type="application/json"
        )
