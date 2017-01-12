#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from django import forms
from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.db.models import Q
from django.template.response import TemplateResponse
from django.shortcuts import (
    redirect, get_object_or_404, render, render_to_response)
from django.template import RequestContext

from pprint import pprint

from actstream.models import Action
from geonode.eula.models import AnonDownloader

from geonode.reports.models import DownloadCount
from collections import OrderedDict, Counter

import urllib2, json
from urllib2 import HTTPError
from datetime import datetime

def report_layer(request, template='reports/report_layers.html'):

    monthly_count = {}
    monthly_list = DownloadCount.objects.filter(chart_group='monthly').order_by('date')
    for eachinlist in monthly_list:
        if eachinlist.date.strftime('%Y%m') not in monthly_count:
            monthly_count[eachinlist.date.strftime('%Y%m')] = {}
        if eachinlist.download_type not in monthly_count[eachinlist.date.strftime('%Y%m')]:
            monthly_count[eachinlist.date.strftime('%Y%m')][eachinlist.download_type] = 0
        monthly_count[eachinlist.date.strftime('%Y%m')][eachinlist.download_type] += eachinlist.count

    luzvimin_count = {}
    luzvimin_list = DownloadCount.objects.filter(chart_group='luzvimin').order_by('date')
    for eachinlist in luzvimin_list:
        if eachinlist.date.strftime('%Y%m') not in luzvimin_count:
            luzvimin_count[eachinlist.date.strftime('%Y%m')] = {}
        if eachinlist.category not in luzvimin_count[eachinlist.date.strftime('%Y%m')]:
            luzvimin_count[eachinlist.date.strftime('%Y%m')][eachinlist.category] = 0
        luzvimin_count[eachinlist.date.strftime('%Y%m')][eachinlist.category] += eachinlist.count

    urls_to_visit = ['https://lipad-fmctst.dream.upd.edu.ph/']
    for each_url in urls_to_visit:
        try:
            response = urllib2.urlopen(each_url + 'api/download_count')
            data = json.loads(response.read())
            objdict = data[u'objects']
            for eachentry in objdict:
                date_of_entry = datetime.strptime(eachentry[u'date'],'%Y-%m-%dT%H:%M:%S').strftime('%Y%m')
                if eachentry[u'chart_group'] == 'monthly':
                    if date_of_entry not in monthly_count:
                        monthly_count[date_of_entry] = {}
                    if eachentry[u'download_type'] not in monthly_count[date_of_entry]:
                        monthly_count[date_of_entry][eachentry[u'download_type']] = 0
                    monthly_count[date_of_entry][eachentry[u'download_type']] += eachentry[u'count']
                elif eachentry[u'chart_group'] == 'luzvimin':
                    if date_of_entry not in luzvimin_count:
                        luzvimin_count[date_of_entry] = {}
                    if eachentry[u'category'] not in luzvimin_count[date_of_entry]:
                        luzvimin_count[date_of_entry][eachentry[u'category']] = 0
                    luzvimin_count[date_of_entry][eachentry[u'category']] += eachentry[u'count']
        except HTTPError:
            continue

    #sorted
    sorted_mc = OrderedDict(sorted(monthly_count.iteritems(), key=lambda x: x[0]))
    sorted_luzvimin = OrderedDict(sorted(luzvimin_count.iteritems(), key=lambda x: x[0]))
    #cumulative
    counter_dict = Counter()
    for each in sorted_mc.iteritems():
        counter_dict.update(each[1])
        sorted_mc[each[0]] = dict(counter_dict)
    #rename
    renamed_mc = OrderedDict([(datetime.strptime(eachone[0],'%Y%m').strftime('%b'),eachone[1]) for eachone in sorted_mc.iteritems()])
    renamed_luzvimin = OrderedDict([(datetime.strptime(eachone[0],'%Y%m').strftime('%b'),eachone[1]) for eachone in sorted_luzvimin.iteritems()])

    reversed_mc = OrderedDict(reversed(list(renamed_mc.items())))
    reversed_luzvimin = OrderedDict(reversed(list(renamed_luzvimin.items())))

    context_dict = {
        "monthly_count": reversed_mc,
        "luzvimin_count": reversed_luzvimin
    }

    return render_to_response(template, RequestContext(request, context_dict))