from django.shortcuts import render,redirect
from .forms.CustomLoginForm import CustomLoginForm
from .forms.SignUpForm import SignUpForm
from django.contrib.auth import authenticate, login, logout
from .models import Category,Book,CartItem,Order,OrderItem,Address
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, CartItem
from .forms.AddressForm import AddressForm
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def login_view(request):
  if request.method == 'POST':
    form = CustomLoginForm(request, data = request.data)
    if form.is_valid():
       username = form.cleaned_data.get('username')
       password = form.cleaned_data.get('password')
       user = authenticate(request, username= username,password = password)

       if user is not None:
         login(user)
         return redirect('home')
  else:
    form = CustomLoginForm()
  
  return render(request,'registration/login.html',{"form":form})



def signup_view(request):
  if request.method == 'POST':
     form = SignUpForm(request.POST)
     if form.is_valid():
        user = form.save()
        login(request,user)
        return redirect('home')
     else:
         print(form.errors) 
  else:
    form = SignUpForm()
  return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")



def home_view(request):
  categories = Category.objects.all()[:6]
  latest_books = Book.objects.order_by('-created_at')[:6]

  return render(request, "ebookapp/home.html", {
      "categories": categories,
      "latest_books": latest_books,
  })


def cart_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {"cart_count": count}


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get("quantity", 1))

    # Check if item already exists in cart
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={"quantity": quantity}
    )
    if not created:
        # Item exists → increase quantity
        cart_item.quantity += quantity
        cart_item.save()

    # Redirect back to the page user came from
    return redirect(request.META.get("HTTP_REFERER", "home"))

@login_required
def cart_view(request):
    """
    Display cart items and total.
    """
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.book.price * item.quantity for item in cart_items)

    return render(request, "ebookapp/cart.html", {"cart_items": cart_items, "total_price": total_price})


@login_required
def update_cart_item(request, item_id):
    """
    Update quantity of a specific cart item.
    """
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect("cart")


@login_required
def remove_cart_item(request, item_id):
    """
    Remove a specific cart item.
    """
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        cart_item.delete()
    return redirect("cart")

@login_required
def checkout_success_view(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "ebookapp/checkout_success.html", {"order": order})




@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("cart")

    if not addresses.exists():
        return redirect("add_address")

    total = sum(item.book.price * item.quantity for item in cart_items)

    if request.method == "POST":
        address_id = request.POST.get("selected_address")

        if not address_id:
            return render(request, "checkout/checkout.html", {
                "error": "Please select a delivery address.",
                "addresses": addresses,
                "cart_items": cart_items,
                "total": total,
            })

        selected_address = Address.objects.get(id=address_id, user=request.user)

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            address=selected_address
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )

        cart_items.delete()

        return redirect("checkout_success", order_id=order.id)

    return render(request, "ebookapp/checkout.html", {
        "addresses": addresses,
        "cart_items": cart_items,
        "total": total,
    })


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "ebookapp/myorder.html", {"orders": orders})


@login_required
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect("address_list")
    else:
        form = AddressForm()
    return render(request, "address/add_address.html", {"form": form})


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, "address/address_list.html", {"addresses": addresses})


@login_required
def edit_address(request, id):
    address = Address.objects.get(id=id, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect("address_list")
    else:
        form = AddressForm(instance=address)

    return render(request, "address/edit_address.html", {"form": form})



@login_required
def delete_address(request, id):
    address = Address.objects.get(id=id, user=request.user)
    address.delete()
    return redirect("address_list")



@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "ebookapp/order_detail.html", {"order": order})


@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    template_path = 'ebookapp/invoice.html'
    context = {'order': order}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response


def book_list_view(request):
    books = Book.objects.all().order_by('title')
    return render(request, "ebookapp/book_list.html", {"books": books})