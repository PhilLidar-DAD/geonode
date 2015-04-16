from django import template
from geonode.cephgeo.models import FTPStatus
register = template.Library()

def get_ftp_status_label(value): # Only one argument.
    """Converts a string into all lowercase"""
    try:
        return FTPStatus.label[value]
    except:
        return "Invalid Status"
