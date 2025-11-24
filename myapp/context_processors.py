def auth_user(request):
    return {
        'user_id': request.session.get('user_id'),
        'user_name': request.session.get('user_name'),
    }
