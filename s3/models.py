from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

PATH_TYPES = (
    ('M', 'matches'),
    ('S', 'starts with'),
)

class BucketPermission(models.Model):
    user = models.ForeignKey(User, related_name='s3_permissions')
    bucket = models.CharField(max_length=255)
    full_access = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user','bucket')
    
    def __unicode__(self):
        return u"%s %s" % (self.user.username, self.bucket)

class PathPermission(models.Model):
    bucket_permission = models.ForeignKey(BucketPermission, related_name="paths")
    type = models.CharField(max_length=1, choices=PATH_TYPES)
    value = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u"%s %s" % (self.type, self.value)
    
    def save(self):
        if self.type == 'S':
            self.value = self.value.lstrip('/')
        super(PathPermission, self).save()