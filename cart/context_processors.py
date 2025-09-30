from .models import Cart

def cart(request):
    if request.user.is_authenticated:
        cart_instance, created = Cart.objects.get_or_create(user=request.user)
        return {'cart': cart_instance}
    return {}
