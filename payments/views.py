from django.http import JsonResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings

import stripe

from cart.models import CartItem
from orders.models import Order, OrderItem


@login_required
@require_POST
def create_checkout_session(request: HttpRequest):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    items = (
        CartItem.objects
        .select_related('product')
        .filter(user=request.user)
        .all()
    )
    if not items:
        return JsonResponse({'error': 'Cart empty'}, status=400)

    line_items = []
    for item in items:
        # Stripe expects amounts in the smallest currency unit
        amount = int(item.product.price * 100)
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': amount,
            },
            'quantity': item.quantity,
        })

    # Shipping flat fee
    shipping_fee = 4900  # ₹49.00 in paise
    line_items.append({
        'price_data': {
            'currency': 'inr',
            'product_data': {'name': 'Shipping'},
            'unit_amount': shipping_fee,
        },
        'quantity': 1,
    })

    session = stripe.checkout.Session.create(
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/orders/checkout/'),
        line_items=line_items,
    )

    return JsonResponse({'id': session.id, 'publicKey': settings.STRIPE_PUBLIC_KEY})


@login_required
def success(request: HttpRequest):
    # On success, capture order in DB and clear cart
    items = (
        CartItem.objects
        .select_related('product')
        .filter(user=request.user)
        .all()
    )
    if not items:
        return redirect('/catalog/')

    subtotal = sum(item.product.price * item.quantity for item in items)
    shipping_fee = 49.00 if subtotal > 0 else 0
    total = subtotal + shipping_fee

    order = Order.objects.create(user=request.user, total_amount=total, status='paid')
    for item in items:
        OrderItem.objects.create(order=order, product=item.product, price=item.product.price, quantity=item.quantity)
    CartItem.objects.filter(user=request.user).delete()

    return redirect(reverse('order_confirmation', args=[order.id]))

# Create your views here.
