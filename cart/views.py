from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages

from .models import CartItem
from catalog.models import Product


@login_required
def cart_detail(request):
    items = (
        CartItem.objects
        .select_related('product')
        .filter(user=request.user)
        .all()
    )
    subtotal = sum(item.product.price * item.quantity for item in items)
    return render(request, 'cart/cart_detail.html', {
        'items': items,
        'subtotal': subtotal,
    })


@login_required
@require_POST
def add_to_cart(request, product_id: int):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        quantity = int(request.POST.get('quantity', '1'))
    except ValueError:
        quantity = 1
    if quantity < 1:
        quantity = 1

    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if created:
        item.quantity = quantity
    else:
        item.quantity += quantity
    item.save()
    messages.success(request, f"Added {product.name} to cart")
    return redirect(request.POST.get('next') or reverse('cart_detail'))


@login_required
@require_POST
def remove_from_cart(request, item_id: int):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.info(request, "Item removed from cart")
    return redirect(reverse('cart_detail'))

# Create your views here.
