from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from ebookapp.models import (
    Category, Book, CartItem,
    Address, Order, OrderItem
)


class TestCategoryModel(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(name="Fiction", slug="fiction")
        self.assertEqual(str(category), "Fiction")

    def test_category_ordering(self):
        Category.objects.create(name="Zebra", slug="zebra")
        Category.objects.create(name="Apple", slug="apple")
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Apple")


class TestBookModel(TestCase):

    def test_book_creation(self):
        category = Category.objects.create(name="SciFi", slug="sci-fi")
        book = Book.objects.create(
            title="Django Magic",
            author="John Doe",
            description="Great book",
            price=Decimal("19.99"),
            stock=5,
            category=category,
            slug="django-magic"
        )
        self.assertEqual(
            str(book),
            "Django Magic by John Doe"
        )


class TestCartItemModel(TestCase):

    def test_cart_item_total_price(self):
        user = User.objects.create_user(username="testuser")
        category = Category.objects.create(name="Tech", slug="tech")
        book = Book.objects.create(
            title="Python 101",
            author="Jane Doe",
            description="Learn Python",
            price=Decimal("10.00"),
            stock=10,
            category=category,
            slug="python-101"
        )

        cart = CartItem.objects.create(user=user, book=book, quantity=3)
        self.assertEqual(cart.total_price(), Decimal("30.00"))

    def test_cart_item_unique_constraint(self):
        user = User.objects.create_user(username="testuser")
        category = Category.objects.create(name="Tech", slug="tech")
        book = Book.objects.create(
            title="Python 101",
            author="Jane Doe",
            description="Learn Python",
            price=Decimal("10.00"),
            stock=10,
            category=category,
            slug="python-101"
        )

        CartItem.objects.create(user=user, book=book, quantity=1)

        with self.assertRaises(Exception):
            CartItem.objects.create(user=user, book=book, quantity=2)


class TestAddressModel(TestCase):

    def test_address_creation(self):
        user = User.objects.create_user(username="john")
        address = Address.objects.create(
            user=user,
            full_name="John Doe",
            phone="1234567890",
            address_line1="Street 1",
            city="Mumbai",
            state="MH",
            pincode="400001"
        )
        self.assertEqual(str(address), "John Doe - Mumbai")


class TestOrderModel(TestCase):

    def test_order_creation(self):
        user = User.objects.create_user(username="testuser")

        order = Order.objects.create(
            user=user,
            total_amount=Decimal("100.00")
        )

        self.assertIn("Order #", str(order))
        self.assertIn("testuser", str(order))


class TestOrderItemModel(TestCase):

    def test_order_item_creation(self):
        user = User.objects.create_user(username="testuser")
        category = Category.objects.create(name="History", slug="history")
        book = Book.objects.create(
            title="Ancient Tales",
            author="Author X",
            description="History content",
            price=Decimal("50.00"),
            stock=5,
            category=category,
            slug="ancient-tales"
        )
        order = Order.objects.create(
            user=user,
            total_amount=Decimal("50.00")
        )

        item = OrderItem.objects.create(
            order=order,
            book=book,
            quantity=2,
            price=Decimal("50.00")
        )

        self.assertEqual(str(item), "Ancient Tales x 2")
