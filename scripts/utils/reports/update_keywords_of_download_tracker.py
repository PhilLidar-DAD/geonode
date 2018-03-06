from geonode.settings import GEONODE_APPS
from geonode.layers.models import Layer
from geonode.reports.models import DownloadCount, SUCLuzViMin, DownloadTracker


downloadtrackerlist = DownloadTracker.objects.all()

for eachdltracked in downloadtrackerlist:
    typename = eachdltracked.title
    print typename
    print eachdltracked.keywords
    try:
        eachdltracked.keywords = Layer.objects.get(typename=typename).keywords.slugs()
    except:
        try:
            eachdltracked.keywords = Layer.objects.get(title=typename).keywords.slugs()
        except:
            continue
    print eachdltracked.keywords
    eachdltracked.save()
