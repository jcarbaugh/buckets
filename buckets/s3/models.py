from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

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
    value = models.CharField(max_length=255)
    
    class Meta:
        ordering = ('value',)
    
    def __unicode__(self):
        return self.value
    
    def save(self):
        self.value = self.value.strip('/')
        super(PathPermission, self).save()