from geonode.settings import GEONODE_APPS
import geonode.settings as settings
from geonode.layers.models import Layer
from geoserver.catalog import Catalog
from geonode.layers.models import Style
import subprocess
import os
import getpass
from geonode.geoserver.helpers import ogc_server_settings
from geonode.base.models import TopicCategory
from guardian.shortcuts import assign_perm, get_anonymous_user
from guardian.shortcuts import get_users_with_perms, remove_perm, get_groups_with_perms
from django.contrib.auth.models import Group
import traceback
from geonode.layers.utils import create_thumbnail


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")

cat = Catalog(settings.OGC_SERVER['default']['LOCATION'] + 'rest',
              username=settings.OGC_SERVER['default']['USER'],
              password=settings.OGC_SERVER['default']['PASSWORD'])


def remove_all_permissions(self):
    """
    Remove all the permissions for users and groups except for the resource owner
    """
    # TODO refactor this
    # first remove in resourcebase
    for user, perms in get_users_with_perms(self.get_self_resource(), attach_perms=True).iteritems():
        if not self.owner == user:
            for perm in perms:
                remove_perm(perm, user, self.get_self_resource())

    for group, perms in get_groups_with_perms(self.get_self_resource(), attach_perms=True).iteritems():
        for perm in perms:
            remove_perm(perm, group, self.get_self_resource())

    # now remove in layer (if resource is layer
    if hasattr(self, "layer"):
        for user, perms in get_users_with_perms(self.layer, attach_perms=True).iteritems():
            if not self.owner == user:
                for perm in perms:
                    remove_perm(perm, user, self.layer)

        for group, perms in get_groups_with_perms(self.layer, attach_perms=True).iteritems():
            for perm in perms:
                remove_perm(perm, group, self.layer)


def fhm_perms_update(layer):

    try:
        # geoadmin = User.objects.get.filter(username='geoadmin')
        # for user in User.objects.all():
        print 'UPDATING PERMISSIONS'
        print layer.name
        remove_all_permissions(layer)
        get_users_with_perms(layer)
        dad_superuser = Group.objects.get(
            name='data-archiving-and-distribution-component')
        assign_perm('view_resourcebase', dad_superuser,
                    layer.get_self_resource())
        assign_perm('download_resourcebase', dad_superuser,
                    layer.get_self_resource())

        assign_perm('view_resourcebase', dad_superuser,
                    layer.get_self_resource())
        assign_perm('download_resourcebase', dad_superuser,
                    layer.get_self_resource())
        print 'FINISHED PERMISSIONS'
    except:
        Err_msg = " Error in updating perms of " + layer.name + "\n"
        print Err_msg
        traceback.print_exc()
        pass


def own_thumbnail(uuid):
    print 'OWNING THUBMNAIL'
    print 'USER', getpass.getuser()
    thumbnail_str = 'layer-' + str(uuid) + '-thumb.png'
    thumb_url = '/var/www/geonode/uploaded/thumbs/' + thumbnail_str
    command_array = ['sudo', '/bin/chown', 'www-data:www-data', thumb_url]
    subprocess.call(command_array)
    command_array = ['sudo', '/bin/chmod', '666', thumb_url]
    subprocess.call(command_array)
    print 'FINISHED THUBMNAIL'


def style_update(layer, style_template):
    print 'UPDATING STYLE'
    cat = Catalog(settings.OGC_SERVER['default']['LOCATION'] + 'rest',
                  username=settings.OGC_SERVER['default']['USER'],
                  password=settings.OGC_SERVER['default']['PASSWORD'])
    gs_layer = cat.get_layer(layer.name)
    print "GS LAYER: ", gs_layer.name

    attributes = [a.attribute for a in layer.attributes]
    style = None
    if 'fh' in layer.name:
        if 'Var' in attributes:
            style = cat.get_style(style_template)
        elif 'Merge' in attributes:
            style = cat.get_style("fhm_merge")
    else:
        style = cat.get_style(style_template)

    if style is not None:
        try:

            gs_layer._set_default_style(style)
            cat.save(gs_layer)
            gs_style = cat.get_style(layer.name)
            if gs_style:
                print "GS STYLE: " % gs_style.name
                print "Geoserver: Will delete style", gs_style.name
                cat.delete(gs_style)
                gn_style = Style.objects.get(name=layer.name)
                print "Geonode: Will delete style ", gn_style.name
                gn_style.delete()

            layer.sld_body = style.sld_body
            layer.save()
        except Exception as e:
            print "Error setting style"

    print 'FINISHED STYLE'


def trees():
    # count_notification = Template(
    #     '[$ctr/$total] Editing Metadata for Layer: $layername')

    ###
    #   TREES - DBH (diameter at breast height) and Standing Tree Volume Estimation
    #   with sld template
    ###
    filter_substring = '_trees'
    layer_list = Layer.objects.filter(name__icontains=filter_substring)
    if layer_list is not None:
        try:
            total = len(layer_list)
            ctr = 0
            identifier = "biota"
            # title = Template(
            #     '$area DBH (diameter at breast height) and Standing Tree Volume Estimation')
            for layer in layer_list:
                ctr += 1
                print "Layer: %s" % layer.name
                style_update(layer, 'trees_template')
                create_thumbnail(layer, layer.get_thumbnail_url())
                own_thumbnail(layer.uuid)
                text_split = layer.name.split(filter_substring)
                area = text_split[0].title().replace('_', ' ')
                # print count_notification.substitute(ctr=ctr, total=total, layername=layer.name)
                # layer.title = title.substitute(area=area)
                layer.title = layer.name.replace('_', ' ').replace(
                    'trees', 'DBH (diameter at breast height) and Standing Tree Volume Estimation').title()
                layer.abstract = """These are points that display the estimated diameter at breast height (DBH) of a forested area. It shows the percentage of trees per dbh class (in cm).

                These are points that display the estimated tree volume of a forested area. It shows the percentage of trees per volume class (in cum)
                """
                layer.purpose = "Forest Resources Assesment/Management"
                layer.keywords.add("FRExLS", " Trees", " DBH",
                                   "Standing Tree Volume", "PhilLiDAR2")
                layer.category = TopicCategory.objects.get(
                    identifier=identifier)
                layer.save()
        except Exception as e:
            print "%s" % e
            pass


def ccm():
    filter_substring = '_ccm'
    layer_list = Layer.objects.filter(name__icontains=filter_substring)
    if layer_list is not None:
        try:
            total = len(layer_list)
            ctr = 0
            identifier = "biota"
            # title = Template('$area Canopy Cover Model')

            for layer in layer_list:
                ctr += 1
                print "Layer: %s" % layer.name
                style_update(layer, layer.name)
                create_thumbnail(layer, layer.get_thumbnail_url())
                own_thumbnail(layer.uuid)
                text_split = layer.name.split(filter_substring)
                area = text_split[0].title().replace('_', ' ')
                # print count_notification.substitute(ctr=ctr, total=total, layername=layer.name)
                # layer.title = title.substitute(area=area)
                layer.title = layer.name.replace('_', ' ').replace(
                    'ccm', ' Canopy Cover Model').title()
                layer.abstract = "These are rasters, with resolution of 1 meter, that display the canopy cover of a forested area. It shows Canopy Cover % which ranges from Low to High"
                layer.purpose = "Forest Resources Assesment/Management"
                layer.keywords.add("FRExLS", "Canopy Cover", "PhilLiDAR2")
                layer.category = TopicCategory.objects.get(
                    identifier=identifier)
                layer.save()
        except Exception as e:
            print "%s" % e
            pass


def chm():
    filter_substring = '_chm'
    layer_list = Layer.objects.filter(name__icontains=filter_substring)
    if layer_list is not None:
        try:
            total = len(layer_list)
            ctr = 0
            identifier = "biota"
            # title = Template('$area Canopy Height Model')

            for layer in layer_list:
                ctr += 1
                print "Layer: %s" % layer.name
                style_update(layer, layer.name)
                create_thumbnail(layer, layer.get_thumbnail_url())
                own_thumbnail(layer.uuid)
                text_split = layer.name.split(filter_substring)
                area = text_split[0].title().replace('_', ' ')
                # print count_notification.substitute(ctr=ctr, total=total, layername=layer.name)
                # layer.title = title.substitute(area=area)
                layer.title = layer.name.replace('_', ' ').replace(
                    'chm', 'Canopy Height Model').title()
                layer.abstract = "These are rasters, with resolution of 1 meter, that display the canopy height of a forested area.It shows the height of trees/vegetation (in meter) present in the sample area"
                layer.purpose = "Forest Resources Assesment/Management"
                layer.keywords.add("FRExLS", "Canopy Height", "PhilLiDAR2")
                layer.category = TopicCategory.objects.get(
                    identifier=identifier)
                layer.save()
        except Exception as e:
            print "%s" % e
            pass


def agb():
    filter_substring = "_agb"
    layer_list = Layer.objects.filter(name__icontains=filter_substring)
    if layer_list is not None:
        try:
            total = len(layer_list)
            ctr = 0
            identifier = "biota"
            # title = Template('$area Biomass Estimation')

            for layer in layer_list:
                ctr += 1
                print "Layer: %s" % layer.name
                style_update(layer, layer.name)
                create_thumbnail(layer, layer.get_thumbnail_url())
                own_thumbnail(layer.uuid)
                text_split = layer.name.split(filter_substring)
                area = text_split[0].title().replace('_', ' ')
                # print count_notification.substitute(ctr=ctr, total=total, layername=layer.name)
                # layer.title = title.substitute(area=area)
                layer.title = layer.name.replace('_', ' ').replace(
                    'agb', 'Biomass Estimation').title()
                layer.abstract = "These are rasters, with a resolution of 10 meters, that display the estimated biomass of a forested area. It shows the total biomass (in kg) per 10sqm of the selected area."
                layer.purpose = "Forest Resources Assesment/Management"
                layer.keywords.add("FRExLS", "Biomass", "PhilLiDAR2")
                layer.category = TopicCategory.objects.get(
                    identifier=identifier)
                layer.save()
        except Exception as e:
            print "%s" % e
            pass


def others(filter_substring):
    layer_list = Layer.objects.filter(name__icontains=filter_substring)
    for layer in layer_list:
        fhm_perms_update(layer)


other_rl = ['_aquaculture', '_aquaculture', '_mangroves',
            '_agrilandcover', '_agricoastlandcover', '_irrigation', '_streams',
            '_wetlands', '_power']
for o in other_rl:
    print o
    others(o)
# trees()
# ccm()
# chm()
