from base64 import b64decode
from boto.s3.key import Key
from boto.s3.prefix import Prefix
from buckets.s3.models import BucketPermission
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
import mimetypes
import re

def load_permissions(user):
    """ Load permissions from database into data structure.
    """
    
    perms = {}  # dict to hold permissions
    
    # iterate over all bucket permissions for the user
    bucket_perms = BucketPermission.objects.filter(user=user)
    for bp in bucket_perms:
        
        # dict to hold bucket-specific permissions
        # full_access == True gives read/write access to entire bucket
        perms[bp.bucket] = {
            'tree': {},
            'full_access': bp.full_access,
        }
        
        # iterate over the user/bucket path permissions
        for pp in bp.paths.all():
            
            node = perms[bp.bucket]['tree']
            
            # iterate over parts of the permission path
            for d in pp.value.split('/'):
                # add current part to tree
                if d not in node:
                    node[d] = {}
                node = node[d]
            
            # add * at end of path to indicate end of permission
            node['*'] = True
    
    return perms
            

def has_permission(user, perms, bucket, path=None):
    """ Test to see if a user has permission to access a bucket
        and or an associate path on the bucket.
    """
    
    # superusers have read/write access to everything
    if user.is_superuser:
        return (True, True)

    # no access if bucket is not in list of permissions
    if bucket not in perms:
        return (False, False)
    
    # If path is not specified, allow read_access since we've already
    # established that the user has bucket permission. Allow write
    # access only if user has full_access permission set.
    if not path or perms[bucket]['full_access']:
        return (True, perms[bucket]['full_access'])
    
    # make path safe and standardized
    path = ('' if path is None else path).strip('/')
    
    # get bucket's permission tree
    node = perms[bucket]['tree']
    
    # iterate over parts of current path
    for d in path.split('/'):
        
        # test to see if part is in permission tree
        node = node.get(d, None)
        
        if node is None:
            # no read/write access if current path is not in tree
            return (False, False)
            
        if '*' in node:
            # allow read/write if we've reached a full permission path
            return (True, True)
    
    # If we've gotten this far then we have permission on a subdirectory
    # of the current directory. Allow reads but no writes.
    return (True, False)

def load_buckets(request):
    if request.user.is_superuser:
        buckets = [b.name for b in request.s3.get_all_buckets()]
    else:
        buckets = [p.bucket for p in request.user.s3_permissions.all()]
    return buckets

@login_required
def bucket_list(request):
    buckets = load_buckets(request)
    request.session['buckets'] = buckets
    request.session['perms'] = load_permissions(request.user)
    return render_to_response('list_buckets.html', {'buckets': buckets},
                              context_instance=RequestContext(request))

@login_required
def list(request, bucket, path=None):
    
    perms = request.session['perms']
    
    (can_read, can_write) = has_permission(request.user, perms, bucket, path)
    if not can_read:
        return HttpResponseForbidden('%s does not have access to %s/%s' % (request.user.email, bucket, path or '')) 
    
    if 'buckets' not in request.session:
        request.session['buckets'] = load_buckets(request)
    
    path = (('' if path is None else path) + '/').lstrip('/')
    path_parts = path.strip('/').split('/')
    
    if request.method == 'POST':
        return upload(
                request,
                bucket,
                path + request.POST.get('filename'),
                b64decode(request.POST.get('data')))

    b = request.s3.get_bucket(bucket)
    
    pl = len(path)

    files = []
    directories = []

    for l in b.list(path or '', delimiter='/'):
        if l.name != path:
            f = {'name': l.name[pl:], 'path': l.name.strip('/')}
            if isinstance(l, Prefix):
                (can_subdir_read, can_subdir_write) = has_permission(request.user, perms, bucket, l.name)
                if can_subdir_read:
                    f['can_read'] = can_subdir_read
                    f['can_write'] = can_subdir_write
                    directories.append(f)
            elif can_write:
                f['mimetype'] = mimetypes.guess_type(f['name'])[0]
                files.append(f)
    
    path_list = []
    tmp_path = ''
    for p in path_parts:
        tmp_path = ('%s/%s' % (tmp_path, p)).strip('/')
        path_list.append({
            'name': p,
            'path': tmp_path.strip('/'),
        })

    params = {
        'buckets': request.session['buckets'],
        'bucket': bucket,
        'path': path,
        'path_list': path_list,
        'directories': directories,
        'can_read': can_read,
        'can_write': can_write,
        'files': files,
        'parent': path_parts[-2] if len(path_parts) > 1 else bucket,
        'parent_path': "/".join(path_parts[:-1]),
        'pwd': path_parts[-1],
    }
    
    if 'json' in request.GET:
        return HttpResponse(json.dumps(params), mimetype='application/json')
    elif 'partial' in request.GET:
        return render_to_response('list.html', params)
    else:
        return render_to_response('list_bucket.html', params,
                                  context_instance=RequestContext(request))

def upload(request, bucket, key, data):
    
    if not key or key.endswith('/'):
        raise ValueError('key required for upload')
        
    perms = request.session['perms']
    (can_read, can_write) = has_permission(request.user, perms, bucket, key)
    
    if not can_write:
        return HttpResponseForbidden('%s does not have access to %s/%s' % (request.user.email, bucket, key or ''))
    
    b = request.s3.get_bucket(bucket)
    k = Key(bucket=b, name=key)
    
    if k.exists() and 'force' not in request.GET:
        raise HttpResponseForbidden('write failed: file exists')
    
    headers = {
        "x-amz-acl": "public-read",
        "Content-Length": len(data),
    }
    
    ct = mimetypes.guess_type(key)[0]
    if ct is not None:
        headers["Content-Type"] = ct
    
    k.set_contents_from_string(data, headers=headers)
    k.set_metadata('uploaded-by', request.user.email)
    
    if request.is_ajax():
        return HttpResponse('{}')
    else:
        return redirect('/' + '/'.join(path.split('/')[:-1]))
    