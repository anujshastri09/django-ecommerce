import razorpay
import stripe
from django.conf import settings
from django.conf import settings
from django.shortcuts import render, redirect,get_object_or_404
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, completed=False)
    item, created = OrderItem.objects.get_or_create(order=order, product=product)
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required
def cart(request):
    order, created = Order.objects.get_or_create(
        user=request.user,
        completed=False
    )
    return render(request, 'store/cart.html', {'order': order})


@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('cart')


@login_required
def remove_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    order = Order.objects.get(user=request.user, completed=False)

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order.address = address
        order.phone = phone
        order.completed = True
        order.save()

        return redirect('success')

    return render(request, 'store/checkout.html', {'order': order})


@login_required
def success(request):
    return render(request, 'store/success.html')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, completed=True)
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required
def checkout(request):
    order = Order.objects.get(user=request.user, completed=False)

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order.address = address
        order.phone = phone
        order.save()

        # Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        payment = client.order.create({
            "amount": int(sum([item.product.price * item.quantity for item in order.orderitem_set.all]) * 100),  # in paise
            "currency": "INR",
            "payment_capture": "1"
        })

        # save order id in session
        request.session['razorpay_order_id'] = payment['id']
        request.session['order_id'] = order.id

        return render(request, 'store/payment.html', {'payment': payment, 'order': order, 'razorpay_key': settings.RAZORPAY_KEY_ID})

    return render(request, 'store/checkout.html', {'order': order})

@login_required
def stripe_checkout(request):
    order = Order.objects.get(user=request.user, completed=False)

    total_amount = int(sum([item.product.price * item.quantity for item in order.orderitem_set.all]) * 100)  # cents

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item.product.name},
                'unit_amount': int(item.product.price*100),  # cents
            },
            'quantity': item.quantity,
        } for item in order.orderitem_set.all()],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cart/'),
    )

    return redirect(session.url)