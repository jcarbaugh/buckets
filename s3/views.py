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

def has_permission(user, bucket, path=None):
    
    if user.is_superuser:
        return True
    
    is_permitted = False
    
    try:
        bp = BucketPermission.objects.get(user=user, bucket=bucket)
    except BucketPermission.DoesNotExist:
        return False
    
    if not path or bp.full_access:
        return True
    
    is_allowed = False
    path = ('' if path is None else path).strip('/')
    
    for pp in bp.paths.all():
        if pp.type == 'M':
            is_allowed = is_allowed or re.match(pp.value, path)
        elif pp.type == 'S':
            is_allowed = is_allowed or path.startswith(pp.value)
    
    return is_allowed

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
    return render_to_response('list_buckets.html', {'buckets': buckets},
                              context_instance=RequestContext(request))

@login_required
def list(request, bucket, path=None):
    
    if not has_permission(request.user, bucket, path):
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
                if has_permission(request.user, bucket, l.name):
                    directories.append(f)
            else:
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
    
    b = request.s3.get_bucket(bucket)
    k = Key(bucket=b, name=key)
    
    if k.exists() and 'force' not in request.GET:
        raise ValueError('file exists')
    
    headers = {
        "x-amz-acl": "public-read",
        "Content-Length": len(data),
        "Content-Type": mimetypes.guess_type(key)[0],
    }
    
    k.set_contents_from_string(data, headers=headers)
    k.set_metadata('uploaded-by', request.user.email)
    
    if request.is_ajax():
        return HttpResponse('{}')
    else:
        return redirect('/' + '/'.join(path.split('/')[:-1]))
    