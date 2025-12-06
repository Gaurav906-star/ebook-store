from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from .forms.CustomLoginForm import CustomLoginForm
from .forms.SignUpForm import SignUpForm
from .models import Category,Book,CartItem,Order,OrderItem,Address
from .forms.AddressForm import AddressForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {"form": form})



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
  categories = Category.objects.all()[:6]    # pylint: disable=no-member
  latest_books = Book.objects.order_by('-created_at')[:6]   # pylint: disable=no-member

  return render(request, "ebookapp/home.html", {
      "categories": categories,
      "latest_books": latest_books,
  })


def cart_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()  # pylint: disable=no-member
    else:
        count = 0
    return {"cart_count": count}


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get("quantity", 1))

    # Check if item already exists in cart
    cart_item, created = CartItem.objects.get_or_create(    # pylint: disable=no-member
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
    cart_items = CartItem.objects.filter(user=request.user)   # pylint: disable=no-member
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
    order = Order.objects.get(id=order_id, user=request.user)  # pylint: disable=no-member
    return render(request, "ebookapp/checkout_success.html", {"order": order})




@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user) # pylint: disable=no-membe
    addresses = Address.objects.filter(user=request.user) # pylint: disable=no-membe

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

        selected_address = Address.objects.get(id=address_id, user=request.user) # pylint: disable=no-membe

        order = Order.objects.create( # pylint: disable=no-membe
            user=request.user,
            total_amount=total,
            address=selected_address
        )

        for item in cart_items:
            OrderItem.objects.create( # pylint: disable=no-membe
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
    orders = Order.objects.filter(user=request.user).order_by("-created_at") # pylint: disable=no-membe
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

    # PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Create PDF canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(30 * mm, 270 * mm, "Invoice")

    # Order info
    p.setFont("Helvetica", 12)
    p.drawString(30 * mm, 260 * mm, f"Order ID: {order.id}")
    p.drawString(30 * mm, 250 * mm, f"Customer: {order.user.get_full_name()}")
    p.drawString(30 * mm, 240 * mm, f"Email: {order.user.email}")
    p.drawString(30 * mm, 230 * mm, f"Date: {order.created_at.strftime('%Y-%m-%d')}")

    # Table header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30 * mm, 210 * mm, "Item")
    p.drawString(120 * mm, 210 * mm, "Price")

    y = 200 * mm

    # Order items
    p.setFont("Helvetica", 12)
    for item in order.items.all():
        p.drawString(30 * mm, y, item.book.title)
        p.drawString(120 * mm, y, f"${item.price}")
        y -= 10 * mm

    # Total
    p.setFont("Helvetica-Bold", 13)
    p.drawString(30 * mm, y - 10 * mm, f"Total: ${order.total_amount}")

    # Finish PDF
    p.showPage()
    p.save()

    return response


def book_list_view(request):
    books = Book.objects.all().order_by('title')
    return render(request, "ebookapp/book_list.html", {"books": books})