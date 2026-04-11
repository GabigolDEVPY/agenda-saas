def global_uid(request):
    uid = request.session.get('uid')
    return {'uid': uid}