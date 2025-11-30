from .models import Favorites, Users

def auth_user(request):
    context = {
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_name': request.user.username if request.user.is_authenticated else None,
        'total_favorites': 0,
    }

    # Calculate favorites count safely
    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            context['total_favorites'] = Favorites.objects.filter(user_ID=user_obj).count()
        except Users.DoesNotExist:
            context['total_favorites'] = 0

    return context