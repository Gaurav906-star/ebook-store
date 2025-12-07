from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ebookapp.models import Book, Category, CartItem, Address, Order, OrderItem


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")

        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Sample Book",
            author="Author",
            price=50,
            stock=10,
            category=self.category
        )

    # ---------- LOGIN VIEW ----------
    def test_login_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_post_success(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 302)

    def test_login_post_failure(self):
        response = self.client.post(reverse("login"), {
            "username": "wrong",
            "password": "wrong"
        })
        self.assertEqual(response.status_code, 200)

    # ---------- SIGNUP VIEW ----------
    def test_signup_view(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    # ---------- LOGOUT ----------
    def test_logout_view(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)

    # ---------- HOME ----------
    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    # ---------- CART ----------
    def test_add_to_cart(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("add_to_cart", args=[self.book.id]), {"quantity": 2})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_cart_view(self):
        self.client.login(username="testuser", password="password123")
        CartItem.objects.create(user=self.user, book=self.book, quantity=1)
        response = self.client.get(reverse("cart"))
        self.assertEqual(response.status_code, 200)

    # ---------- ADDRESS ----------
    def test_add_address(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("add_address"), {
            "full_name": "Test User",
            "phone": "1234567890",
            "address_line1": "Line1",
            "address_line2": "Line2",
            "city": "City",
            "state": "State",
            "pincode": "111111",
            "country": "Country"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Address.objects.count(), 1)

    # ---------- CHECKOUT ----------
    def test_checkout_flow(self):
        self.client.login(username="testuser", password="password123")
        CartItem.objects.create(user=self.user, book=self.book, quantity=2)
        address = Address.objects.create(
            user=self.user,
            full_name="Test User",
            phone="1234567890",
            address_line1="Line1",
            city="City",
            state="State",
            pincode="111111",
            country="Country"
        )

        response = self.client.post(reverse("checkout"), {
            "selected_address": address.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

    # ---------- MY ORDERS ----------
    def test_my_orders_view(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("my_orders"))
        self.assertEqual(response.status_code, 200)

    # ---------- BOOK LIST ----------
    def test_book_list_view(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
