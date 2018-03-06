#!/usr/bin/#!/usr/bin/env python

import geojson
import logging
import os
import requests
import geonode.settings as settings
from geonode.cephgeo.gsquery import nested_grid_update

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")


logger = logging.getLogger('zero_philgrid.py')
hdlr = logging.FileHandler('zero-out-philgrid.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%b %d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def grid_feature_update(gridref_dict_by_data_class, field_value=0):
    """
        :param gridref_dict_by_data_class: contains mapping of [feature_attr]
        to [grid_ref_list]
        :param field_value: [1] or [0]
        Update the grid shapefile feature attribute specified by [feature_attr]
        on gridrefs in [gridref_list]
    """

    # print 'GRIDREF DICT BY DATA CLASS'
    # print gridref_dict_by_data_class
    # sample
    # {'LAZ':
    #     ['E232N1745', 'E231N1744', 'E231N1745', 'E232N1744', 'E232N1744',
    #     'E230N1745', 'E232N1745', 'E231N1744', 'E231N1745', 'E230N1745']
    #

    x = 0
    for feature_attr, grid_ref_list in gridref_dict_by_data_class.iteritems():
        print "Updating feature attribute [{0}]".format(feature_attr)
        print 'INDEX NESTED GRID UPDATE:', x
        grid_ref_chunks = chunks(grid_ref_list, 512)
        chunk_ct = 1
        for grid_ref_chunk in grid_ref_chunks:
            logger.info("Feature: {0} GRIDREF: {1}".format(feature_attr, grid_ref_chunk))
            logger.info("Task for feature [{0}] chunk [{1}]".format(feature_attr, chunk_ct))
            philgrid_update_result = nested_grid_update(grid_ref_chunk, feature_attr, field_value)
            if not philgrid_update_result:
                logger.error('philgrid_update_result:', philgrid_update_result)
            else:
                logger.info("Finished task for feature [{0}] chunk [{1}]".format(feature_attr, chunk_ct))
            chunk_ct = chunk_ct + 1


def main():
    logger.info("Start script")
    logger.info("Loading philgrid json from https://lipad.dream.upd.edu.ph/geoserver/wfs?srsName=EPSG%3A4326&typename=geonode%3Aphilgrid&outputFormat=json&version=1.0.0&service=WFS&request=GetFeature")
    r = requests.get('http://127.0.0.1/geoserver/wfs?srsName=EPSG%3A4326&typename=geonode%3Aphilgrid&outputFormat=json&version=1.0.0&service=WFS&request=GetFeature')
    c = r.content
    philgrid_json = geojson.loads(c)
    gridref_dict_by_data_class = dict()
    ortho_ct = 0
    laz_ct = 0
    dsm_ct = 0
    dtm_ct = 0
    for feature in philgrid_json['features']:
        gridref = feature['properties']['GRIDREF']
        if feature['properties']['ORTHO'] == 1:
            ortho_ct = ortho_ct + 1
            if 'ORTHO'.encode('utf8') in gridref_dict_by_data_class:
                gridref_dict_by_data_class['ORTHO'.encode('utf8')].append(gridref.encode('utf8'))
            else:
                gridref_dict_by_data_class['ORTHO'.encode('utf8')] = [gridref.encode('utf8'), ]
        elif feature['properties']['LAZ'] == 1:
            laz_ct = laz_ct + 1
            if 'LAZ'.encode('utf8') in gridref_dict_by_data_class:
                gridref_dict_by_data_class['LAZ'.encode('utf8')].append(gridref.encode('utf8'))
            else:
                gridref_dict_by_data_class['LAZ'.encode('utf8')] = [gridref.encode('utf8'), ]
        elif feature['properties']['DSM'] == 1:
            dsm_ct = dsm_ct + 1
            if 'DSM'.encode('utf8') in gridref_dict_by_data_class:
                gridref_dict_by_data_class['DSM'.encode('utf8')].append(gridref.encode('utf8'))
            else:
                gridref_dict_by_data_class['DSM'.encode('utf8')] = [gridref.encode('utf8'), ]
        elif feature['properties']['DTM'] == 1:
            dtm_ct = dtm_ct + 1
            if 'DTM'.encode('utf8') in gridref_dict_by_data_class:
                gridref_dict_by_data_class['DTM'.encode('utf8')].append(gridref.encode('utf8'))
            else:
                gridref_dict_by_data_class['DTM'.encode('utf8')] = [gridref.encode('utf8'), ]
    logger.info("ORTHO: {0}".format(ortho_ct))
    logger.info("LAZ: {0}".format(laz_ct))
    logger.info("DSM: {0}".format(dsm_ct))
    logger.info("DTM: {0}".format(dtm_ct))
    grid_feature_update(gridref_dict_by_data_class, 0)


if __name__ == "__main__":
    main()

