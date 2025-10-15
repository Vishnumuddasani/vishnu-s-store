from typing import Dict

from django.contrib.auth.models import AnonymousUser

from cart.models import CartItem


def cart_count(request) -> Dict[str, int]:
    user = getattr(request, 'user', AnonymousUser())
    if not user.is_authenticated:
        return {'cart_count': 0}
    count = CartItem.objects.filter(user=user).count()
    return {'cart_count': count}


