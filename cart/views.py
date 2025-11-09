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
    
    try:
        quantity = float(request.POST.get('quantity', 1))
        unidad_compra = request.POST.get('unidad', publication.unidad_medida)
        
        # Verificar disponibilidad con conversión
        disponible, cantidad_disponible = publication.verificar_disponibilidad(quantity, unidad_compra)
        
        if not disponible:
            messages.error(request, f'❌ Cantidad no disponible. Solo hay {cantidad_disponible:.1f} {unidad_compra} disponibles')
            next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'marketplace'))
            return redirect(next_url)
        
        # Buscar si ya existe item con la misma unidad
        cart_item = CartItem.objects.filter(
            cart=cart,
            publication=publication,
            unidad_compra=unidad_compra
        ).first()
        
        if cart_item:
            # Verificar nueva cantidad
            nueva_cantidad = float(cart_item.quantity) + quantity
            disponible, cantidad_disponible = publication.verificar_disponibilidad(nueva_cantidad, unidad_compra)
            
            if not disponible:
                messages.error(request, f'❌ No puedes agregar esa cantidad. Solo hay {cantidad_disponible:.1f} {unidad_compra} disponibles y ya tienes {float(cart_item.quantity):.1f} en tu carrito')
                next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'marketplace'))
                return redirect(next_url)
            
            cart_item.quantity = nueva_cantidad
            cart_item.save()
            messages.success(request, f'✓ Cantidad actualizada: {publication.cultivo.nombre} ({float(cart_item.quantity):.1f} {unidad_compra})')
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                publication=publication,
                quantity=quantity,
                unidad_compra=unidad_compra
            )
            messages.success(request, f'✓ Producto agregado al carrito: {publication.cultivo.nombre} ({quantity:.1f} {unidad_compra})')
        
    except ValueError:
        messages.error(request, '❌ Cantidad inválida')
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'marketplace'))
        return redirect(next_url)
    
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
    product_name = cart_item.publication.cultivo.nombre
    
    try:
        quantity = float(request.POST.get('quantity'))
        unidad = request.POST.get('unidad', cart_item.unidad_compra)
        
        if quantity > 0:
            # Verificar disponibilidad
            disponible, cantidad_disponible = cart_item.publication.verificar_disponibilidad(quantity, unidad)
            
            if not disponible:
                messages.error(request, f'❌ Cantidad no disponible. Solo hay {cantidad_disponible:.1f} {unidad} disponibles')
                return redirect('cart:cart_detail')
            
            cart_item.quantity = quantity
            cart_item.unidad_compra = unidad
            cart_item.save()
            messages.success(request, f'✓ Cantidad actualizada: {product_name} ({quantity:.1f} {unidad})')
        else:
            cart_item.delete()
            messages.success(request, f'✓ Producto eliminado del carrito: {product_name}')
    except ValueError:
        messages.error(request, '❌ Cantidad inválida')
    
    return redirect('cart:cart_detail')
