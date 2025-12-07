from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from .forms.AddressForm import AddressForm
from .forms.CustomLoginForm import CustomLoginForm
from .forms.SignUpForm import SignUpForm
from .models import Address, Book, CartItem, Category, Order, OrderItem



def login_view(request):
    """
    Handle user login by validating form data and authenticating credentials.
    Redirects authenticated users to home page or re-renders login form on failure.
    """
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            
            messages.error(request, "Invalid username or password.")
            return render(request, 'registration/login.html', {"form": form})
        
        messages.error(request, "Invalid username or password.")
        return render(request, 'registration/login.html', {"form": form})
    
    form = CustomLoginForm()
    return render(request, 'registration/login.html', {"form": form})



def signup_view(request):
  """
    Handle user registration process.
    Creates a new user account and logs the user in upon successful sign-up.
  """
  if request.method == 'POST':
     form = SignUpForm(request.POST)
     if form.is_valid():
        user = form.save()
        login(request,user)
        return redirect('home')
     
     print(form.errors)
     return render(request, "registration/signup.html", {"form": form})
  
  form = SignUpForm()
  return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    """
    Log out the currently authenticated user and redirect to the home page.
    """
    logout(request)
    return redirect("home")



def home_view(request):
  """
    Display homepage with featured categories and latest books.
  """
  categories = Category.objects.all()[:6]    # pylint: disable=no-member
  latest_books = Book.objects.order_by('-created_at')[:6]   # pylint: disable=no-member

  return render(request, "ebookapp/home.html", {
      "categories": categories,
      "latest_books": latest_books,
  })


def cart_count(request):
    """
    Provide cart item count to templates via context processor.
    Returns 0 when user is not authenticated.
    """
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()  # pylint: disable=no-member
    else:
        count = 0
    return {"cart_count": count}


@login_required
def add_to_cart(request, book_id):
    """
    Add a book to the user's shopping cart.
    If the item already exists, its quantity is increased.
    """
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
    """
    To tell user on successful order checkout.
    """
    order = Order.objects.get(id=order_id, user=request.user)  # pylint: disable=no-member
    return render(request, "ebookapp/checkout_success.html", {"order": order})




@login_required
def checkout_view(request):
    """
    Handle checkout process:
    - Validate the cart
    - Validate address selection
    - Create order and order items
    - Clear cart after successful purchase
    """
    cart_items = CartItem.objects.filter(user=request.user) # pylint: disable=no-member
    addresses = Address.objects.filter(user=request.user) # pylint: disable=no-member

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

        selected_address = Address.objects.get(id=address_id, user=request.user) # pylint: disable=no-member
        # Order creation
        order = Order.objects.create( # pylint: disable=no-member
            user=request.user,
            total_amount=total,
            address=selected_address
        )
       # save the Order Item
        for item in cart_items:
            OrderItem.objects.create( # pylint: disable=no-member
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
    """
    To display all the placed order by user
    """
    orders = Order.objects.filter(user=request.user).order_by("-created_at") # pylint: disable=no-member
    return render(request, "ebookapp/myorder.html", {"orders": orders})


@login_required
def add_address(request):
    """
    User can add his/her current address
    """
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
    """
    To list down all user's address 
    """
    addresses = request.user.addresses.all()
    return render(request, "address/address_list.html", {"addresses": addresses})


@login_required
def edit_address(request, id):
    """
    To edit the already saved address
    """
    address = Address.objects.get(id=id, user=request.user) # pylint: disable=no-member

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
    """
    To delete already existing address by address id
    """
    address = Address.objects.get(id=id, user=request.user) # pylint: disable=no-member
    address.delete()
    return redirect("address_list")



@login_required
def order_detail(request, order_id):
    """
    To view the placed order details by order Id
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "ebookapp/order_detail.html", {"order": order})



@login_required
def download_invoice(request, order_id):
    """
    To download the invoice of placed order with order id
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Create PDF canvas
    p = canvas.Canvas(response, pagesize=A4)

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
    """
    it will fetch all the books from DB
    it will pass to html page to show to user in list form
    """
    books = Book.objects.all().order_by('title') # pylint: disable=no-member
    return render(request, "ebookapp/book_list.html", {"books": books})
