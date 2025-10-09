from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from marketplace.models import Publication
from .models import Cart, CartItem
from django.http import HttpResponseRedirect
from django.contrib import messages

# Create your views here.

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@login_required
@require_POST
def add_to_cart(request, publication_id):
    cart = get_object_or_404(Cart, user=request.user)
    publication = get_object_or_404(Publication, id=publication_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        publication=publication,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'✓ Cantidad actualizada: {publication.cultivo.nombre} ({cart_item.quantity} {publication.cultivo.unidad_medida})')
    else:
        messages.success(request, f'✓ Producto agregado al carrito: {publication.cultivo.nombre} ({quantity} {publication.cultivo.unidad_medida})')
    
    # Redirigir de vuelta a la página anterior o al marketplace
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'marketplace'))
    return redirect(next_url)

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.publication.cultivo.nombre
    cart_item.delete()
    messages.success(request, f'✓ Producto eliminado del carrito: {product_name}')
    return redirect('cart:cart_detail')

@login_required
@require_POST
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity'))
    product_name = cart_item.publication.cultivo.nombre
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'✓ Cantidad actualizada: {product_name} ({quantity} {cart_item.publication.cultivo.unidad_medida})')
    else:
        cart_item.delete()
        messages.success(request, f'✓ Producto eliminado del carrito: {product_name}')
    return redirect('cart:cart_detail')
