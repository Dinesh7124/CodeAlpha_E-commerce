from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Category, Product, ProductImage, Order, OrderItem, Review, Wishlist
from .cart import Cart
from .forms import UserRegisterForm, OrderCreateForm, ProductForm, CategoryForm, ReviewForm, ProductImageForm


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')(view_func)


# ===== PUBLIC VIEWS =====

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    query = request.GET.get('q', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    sort = request.GET.get('sort', '-created')
    sort_map = {
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
        'newest': '-created',
    }
    products = products.order_by(sort_map.get(sort, '-created'))

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
        'sort': sort,
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    related = Product.objects.filter(category=product.category, available=True).exclude(id=product.id)[:4]
    reviews = product.reviews.all()
    gallery_images = product.all_images()

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    review_form = ReviewForm()
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            Review.objects.update_or_create(
                product=product, user=request.user,
                defaults={
                    'rating': review_form.cleaned_data['rating'],
                    'comment': review_form.cleaned_data['comment'],
                }
            )
            messages.success(request, 'Review saved!')
            return redirect('store:product_detail', id=product.id, slug=product.slug)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related': related,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review,
        'in_wishlist': in_wishlist,
        'gallery_images': gallery_images,
    })


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect('store:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('store:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('store:product_list')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.get_total_price()
            order.paid = True
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order, product=item['product'],
                    price=item['price'], quantity=item['quantity']
                )
                item['product'].stock -= item['quantity']
                item['product'].save()
            cart.clear()
            return render(request, 'store/order_success.html', {'order': order})
    else:
        form = OrderCreateForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    return render(request, 'store/checkout.html', {'cart': cart, 'form': form})


# ===== WISHLIST =====

@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'items': items})


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        messages.info(request, f'Removed "{product.name}" from wishlist.')
    else:
        messages.success(request, f'Added "{product.name}" to wishlist!')
    return redirect(request.META.get('HTTP_REFERER', 'store:product_list'))


# ===== ORDER HISTORY =====

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# ===== MANAGER =====

@staff_required
def manage_dashboard(request):
    stats = {
        'products': Product.objects.count(),
        'categories': Category.objects.count(),
        'orders': Order.objects.count(),
        'users': User.objects.count(),
        'revenue': sum((o.total for o in Order.objects.all()), 0),
        'low_stock': Product.objects.filter(stock__lt=5).count(),
    }
    recent_orders = Order.objects.all()[:10]
    low_stock = Product.objects.filter(stock__lt=5)[:10]
    return render(request, 'store/manage/dashboard.html', {
        'stats': stats, 'recent_orders': recent_orders, 'low_stock': low_stock,
    })


@staff_required
def manage_products(request):
    products = Product.objects.all().select_related('category').prefetch_related('images')
    return render(request, 'store/manage/products.html', {'products': products})


@staff_required
def manage_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Handle gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for i, img in enumerate(gallery_images):
                ProductImage.objects.create(product=product, image=img, order=i)
            messages.success(request, f'Product "{product.name}" created with {len(gallery_images)} gallery images!')
            return redirect('store:manage_products')
    else:
        form = ProductForm()
    return render(request, 'store/manage/product_form.html', {'form': form, 'title': 'Add Product'})


@staff_required
def manage_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # New gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            existing_count = product.images.count()
            for i, img in enumerate(gallery_images):
                ProductImage.objects.create(product=product, image=img, order=existing_count + i)
            # Handle delete requests
            delete_ids = request.POST.getlist('delete_image')
            if delete_ids:
                ProductImage.objects.filter(id__in=delete_ids, product=product).delete()
            messages.success(request, f'Product "{product.name}" updated!')
            return redirect('store:manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/manage/product_form.html', {
        'form': form, 'title': 'Edit Product', 'product': product
    })


@staff_required
def manage_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('store:manage_products')
    return render(request, 'store/manage/confirm_delete.html', {'object': product, 'type': 'Product'})


@staff_required
def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'store/manage/categories.html', {'categories': categories})


@staff_required
def manage_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created!')
            return redirect('store:manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'store/manage/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_required
def manage_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated!')
            return redirect('store:manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'store/manage/category_form.html', {'form': form, 'title': 'Edit Category'})


@staff_required
def manage_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('store:manage_categories')
    return render(request, 'store/manage/confirm_delete.html', {'object': category, 'type': 'Category'})


@staff_required
def manage_orders(request):
    orders = Order.objects.all().prefetch_related('items')
    return render(request, 'store/manage/orders.html', {'orders': orders})


@staff_required
def manage_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated.')
        return redirect('store:manage_order_detail', order_id=order.id)
    return render(request, 'store/manage/order_detail.html', {'order': order})


@staff_required
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'store/manage/users.html', {'users': users})
