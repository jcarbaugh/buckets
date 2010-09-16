from boto.s3.connection import S3Connection
from django.conf import settings

class S3Middleware(object):
    def process_request(self, request):
        request.s3 = S3Connection(settings.AWS_KEY, settings.AWS_SECRET)