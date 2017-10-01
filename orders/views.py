from django.shortcuts import render
from .models import OrderItem,Order
from shop.models import Product
from .forms import OrderCreateForm
from cart.cart import Cart
from django.http import HttpResponse
from django.template import loader, Context
import copy
from time import gmtime, strftime




def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # clear the cart
            cart.clear()
            return render(request, 'orders/order/created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart,
                                                        'form': form})
def export_csv(request):
	time = str(strftime("%d:%m:%Y_%H:%M:%S", gmtime()))
	filename = "OrderList_" + time + ".csv"
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = str.format('attachment; filename={0}',filename)
	csv_data = [('ID','First Name','Last Name','Address','City','Created','Product','Price','Quantity'),]
	order_list = Order.objects.all()
	for order in order_list:
		base_list = [order.id,order.first_name,order.last_name,order.address,order.city,order.created]
		order_items = OrderItem.objects.filter(order_id=order.id)
		for item in order_items:
			base_list_product = copy.copy(base_list)
			product = Product.objects.get(id=item.product_id)
			base_list_product.append(product.slug)
			base_list_product.append(product.price)
			base_list_product.append(item.quantity)
			csv_data.append(base_list_product)
	t = loader.get_template('csv.txt')
	c = {'data': csv_data,}
	response.write(t.render(c))
	return response
