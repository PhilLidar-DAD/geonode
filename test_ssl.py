#!/opt/geonode/virtualenv/geonode/bin/python

import httplib2
import sys

h = httplib2.Http()
print sys.argv
resp, content = h.request(sys.argv[1])
print "resp:", resp
print "content:", content
