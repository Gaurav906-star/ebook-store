from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from ebookapp.models import (
    Category,
    Book,
    CartItem,
    Address,
    Order,
    OrderItem,
)
from ebookapp.views import cart_count


class BaseViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create user
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username="testuser",
            password=self.password,
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        # Category & Book
        self.category = Category.objects.create(name="Fiction", slug="fiction")
        self.book = Book.objects.create(
            title="Book One",
            author="Author A",
            description="Desc",
            price=Decimal("10.00"),
            stock=10,
            category=self.category,
            slug="book-one",
        )

        # Address
        self.address = Address.objects.create(
            user=self.user,
            full_name="Test User",
            phone="1234567890",
            address_line1="Street 1",
            city="City",
            state="State",
            pincode="123456",
            country="India",
        )


class AuthViewsTests(BaseViewTestCase):
    def test_login_view_get(self):
        url = reverse("login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_view_post_success(self):
        url = reverse("login")

        response = self.client.post(
            url,
            {"username": self.user.username, "password": self.password, "email": self.user.email},
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))


    def test_login_view_post_invalid(self):
        url = reverse("login")
        response = self.client.post(
            url,
            {"username": "wrong", "password": "wrong","email":"wrong@gmail.com"},
            follow=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_signup_view_get(self):
        url = reverse("signup")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_view_post_valid(self):
        url = reverse("signup")
        response = self.client.post(
            url,
            {
                "username": "newuser",
                "password1": "Newpass123!",
                "password2": "Newpass123!",
                "email": "new@example.com",
            },
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_view_post_invalid(self):
        url = reverse("signup")
        response = self.client.post(
            url,
            {
                "username": "x",
                "password1": "a",
                "password2": "b",  # mismatch
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_logout_view(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse("logout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

class HomeAndBookViewsTests(BaseViewTestCase):
    def test_home_view(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("categories", response.context)
        self.assertIn("latest_books", response.context)
        self.assertTemplateUsed(response, "ebookapp/home.html")

    def test_book_list_view(self):
        url = reverse("booklist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ebookapp/book_list.html")
        self.assertIn("books", response.context)


class CartContextProcessorTests(BaseViewTestCase):
    def test_cart_count_anonymous(self):
        class DummyUser:
            is_authenticated = False

        class DummyRequest:
            user = DummyUser()

        context = cart_count(DummyRequest())
        self.assertEqual(context["cart_count"], 0)

    def test_cart_count_authenticated(self):
        # create a cart item
        CartItem.objects.create(user=self.user, book=self.book, quantity=2)

        class DummyRequest:
            user = self.user

        context = cart_count(DummyRequest())
        self.assertEqual(context["cart_count"], 1)


class CartViewsTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    def test_add_to_cart_new_item(self):
        url = reverse("add_to_cart", args=[self.book.id])
        response = self.client.post(
            url,
            {"quantity": 2},
            HTTP_REFERER=reverse("home"),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        cart_item = CartItem.objects.get(user=self.user, book=self.book)
        self.assertEqual(cart_item.quantity, 2)

    def test_add_to_cart_existing_item_increments(self):
        CartItem.objects.create(user=self.user, book=self.book, quantity=1)
        url = reverse("add_to_cart", args=[self.book.id])
        response = self.client.post(
            url,
            {"quantity": 3},
            HTTP_REFERER=reverse("home"),
        )
        self.assertEqual(response.status_code, 302)
        cart_item = CartItem.objects.get(user=self.user, book=self.book)
        self.assertEqual(cart_item.quantity, 4)

    def test_cart_view(self):
        CartItem.objects.create(user=self.user, book=self.book, quantity=2)
        url = reverse("cart")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ebookapp/cart.html")
        self.assertIn("cart_items", response.context)
        self.assertIn("total_price", response.context)
        self.assertEqual(response.context["total_price"], Decimal("20.00"))

    def test_update_cart_item_post(self):
        cart_item = CartItem.objects.create(user=self.user, book=self.book, quantity=1)
        url = reverse("update_cart_item", args=[cart_item.id])
        response = self.client.post(url, {"quantity": 5})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cart"))
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_update_cart_item_get_does_not_change(self):
        cart_item = CartItem.objects.create(user=self.user, book=self.book, quantity=1)
        url = reverse("update_cart_item", args=[cart_item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_remove_cart_item_post(self):
        cart_item = CartItem.objects.create(user=self.user, book=self.book, quantity=1)
        url = reverse("remove_cart_item", args=[cart_item.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cart"))
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

    def test_remove_cart_item_get_does_not_delete(self):
        cart_item = CartItem.objects.create(user=self.user, book=self.book, quantity=1)
        url = reverse("remove_cart_item", args=[cart_item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CartItem.objects.filter(id=cart_item.id).exists())


class CheckoutAndOrderViewsTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    def test_checkout_view_redirects_if_cart_empty(self):
        url = reverse("checkout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cart"))

    def test_checkout_view_redirects_if_no_address(self):
        # remove addresses
        Address.objects.filter(user=self.user).delete()
        CartItem.objects.create(user=self.user, book=self.book, quantity=1)

        url = reverse("checkout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("add_address"))

    def test_checkout_view_get(self):
        CartItem.objects.create(user=self.user, book=self.book, quantity=2)
        url = reverse("checkout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ebookapp/checkout.html")
        self.assertIn("addresses", response.context)
        self.assertIn("cart_items", response.context)
        self.assertIn("total", response.context)

    def test_checkout_view_post_without_address(self):
        CartItem.objects.create(user=self.user, book=self.book, quantity=2)
        url = reverse("checkout")
        response = self.client.post(url, {})  # no selected_address
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ebookapp/checkout.html")
        self.assertIn("error", response.context)

    def test_checkout_view_post_success(self):
        cart_item = CartItem.objects.create(user=self.user, book=self.book, quantity=2)
        url = reverse("checkout")
        response = self.client.post(
            url,
            {"selected_address": self.address.id},
        )
        # Should create Order, OrderItems and clear cart
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=self.user)
        self.assertEqual(response.url, reverse("checkout_success", args=[order.id]))
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
        self.assertEqual(order.items.count(), 1)

    def test_checkout_success_view(self):
        order = Order.objects.create(
            user=self.user,
            address=self.address,
            total_amount=Decimal("20.00"),
        )
        url = reverse("checkout_success", args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ebookapp/checkout_success.html")
        self.assertEqual(response.context["order"], order)

    def test_my_orders_view(self):
        order1 = Order.objects.create(
            user=self.user,
            address=self.address,
            total_amount=Decimal("10.00"),
        )
        order2 = Order.objects.create(
            user=self.user,
            address=self.address,
            total_amount=Decimal("20.00"),
        )
        url = reverse("my_orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ebookapp/myorder.html")
        orders = response.context["orders"]
        self.assertIn(order1, orders)
        self.assertIn(order2, orders)

    def test_order_detail_view(self):
        order = Order.objects.create(
            user=self.user,
            address=self.address,
            total_amount=Decimal("10.00"),
        )
        OrderItem.objects.create(
            order=order,
            book=self.book,
            quantity=1,
            price=self.book.price,
        )
        url = reverse("order_detail", args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ebookapp/order_detail.html")
        self.assertEqual(response.context["order"], order)

    def test_download_invoice_view(self):
        order = Order.objects.create(
            user=self.user,
            address=self.address,
            total_amount=Decimal("10.00"),
        )
        OrderItem.objects.create(
            order=order,
            book=self.book,
            quantity=1,
            price=self.book.price,
        )
        url = reverse("download_invoice", args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"], "application/pdf"
        )
        self.assertIn(
            f'attachment; filename="invoice_{order.id}.pdf"',
            response["Content-Disposition"],
        )
        self.assertGreater(len(response.content), 0)


class AddressViewsTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password=self.password)

    def test_address_list_view(self):
        url = reverse("address_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "address/address_list.html")
        self.assertIn("addresses", response.context)

    def test_add_address_get(self):
        url = reverse("add_address")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "address/add_address.html")

    def test_add_address_post_valid(self):
        url = reverse("add_address")
        response = self.client.post(
            url,
            {
                "full_name": "Another User",
                "phone": "9999999999",
                "address_line1": "Line1",
                "address_line2": "",
                "city": "CityX",
                "state": "StateX",
                "pincode": "654321",
                "country": "India",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("address_list"))
        self.assertTrue(
            Address.objects.filter(user=self.user, full_name="Another User").exists()
        )

    def test_edit_address_get(self):
        url = reverse("edit_address", args=[self.address.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "address/edit_address.html")

    def test_edit_address_post_valid(self):
        url = reverse("edit_address", args=[self.address.id])
        response = self.client.post(
            url,
            {
                "full_name": "Updated Name",
                "phone": "1234567890",
                "address_line1": "Street 1",
                "address_line2": "",
                "city": "City",
                "state": "State",
                "pincode": "123456",
                "country": "India",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("address_list"))
        self.address.refresh_from_db()
        self.assertEqual(self.address.full_name, "Updated Name")

    def test_delete_address_view(self):
        url = reverse("delete_address", args=[self.address.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("address_list"))
        self.assertFalse(Address.objects.filter(id=self.address.id).exists())
