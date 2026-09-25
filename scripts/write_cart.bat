@echo off
(
echo from decimal import Decimal
echo from .models import Product
echo.
echo.
echo class Cart:
echo     def __init__(self, request):
echo         self.session = request.session
echo         cart = self.session.get('cart')
echo         if not cart:
echo             cart = self.session['cart'] = {}
echo         self.cart = cart
echo.
echo     def add(self, product, quantity=1, update_quantity=False):
echo         product_id = str(product.id)
echo         if product_id not in self.cart:
echo             self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
echo         if update_quantity:
echo             self.cart[product_id]['quantity'] = quantity
echo         else:
echo             self.cart[product_id]['quantity'] += quantity
echo         self.save()
echo.
echo     def remove(self, product):
echo         product_id = str(product.id)
echo         if product_id in self.cart:
echo             del self.cart[product_id]
echo             self.save()
echo.
echo     def save(self):
echo         self.session.modified = True
echo.
echo     def __iter__(self):
echo         product_ids = self.cart.keys()
echo         products = Product.objects.filter(id__in=product_ids)
echo         cart = self.cart.copy()
echo         for product in products:
echo             cart[str(product.id)]['product'] = product
echo.
echo         for item in cart.values():
echo             item['price'] = Decimal(item['price'])
echo             item['total_price'] = item['price'] * item['quantity']
echo             yield item
echo.
echo     def __len__(self):
echo         return sum(item['quantity'] for item in self.cart.values())
echo.
echo     def get_total_price(self):
echo         return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
echo.
echo     def clear(self):
echo         del self.session['cart']
echo         self.save()
) > store\cart.py
echo Done - cart.py written