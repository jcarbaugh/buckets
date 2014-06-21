from buckets.s3.models import BucketPermission, PathPermission
from django.contrib import admin

class PathPermissionInline(admin.TabularInline):
    model = PathPermission

class BucketPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'bucket')
    list_display_links = ('bucket',)
    list_filter = ('user',)
    inlines = (PathPermissionInline,)

admin.site.register(BucketPermission, BucketPermissionAdmin)