from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth.models import User

from ebookapp.admin import (
    CategoryAdmin, BookAdmin, CartItemAdmin,
    OrderAdmin, OrderItemAdmin, OrderItemInline
)
from ebookapp.models import Category, Book, CartItem, Order, OrderItem


class AdminConfigTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.site = admin.AdminSite()
      

        # Sample objects
        self.user = User.objects.create(username="testuser")
        self.category = Category.objects.create(name="Fiction", slug="fiction")
        self.book = Book.objects.create(
            title="Test Book",
            author="Author A",
            description="desc",
            price=10.0,
            stock=5,
            category=self.category,
            slug="test-book"
        )
        self.order = Order.objects.create(user=self.user, total_amount=20)
        self.order_item = OrderItem.objects.create(
            order=self.order, book=self.book, quantity=1, price=10
        )
        self.cart_item = CartItem.objects.create(
            user=self.user, book=self.book, quantity=2
        )

    # -------------------------------------------------------------
    # CATEGORY ADMIN TESTS
    # -------------------------------------------------------------
    def test_category_admin_config(self):
        model_admin = CategoryAdmin(Category, self.site)

        self.assertEqual(model_admin.list_display, ("name", "slug"))
        self.assertEqual(model_admin.prepopulated_fields, {"slug": ("name",)})
        self.assertEqual(model_admin.search_fields, ("name",))

    # -------------------------------------------------------------
    # BOOK ADMIN TESTS
    # -------------------------------------------------------------
    def test_book_admin_config(self):
        model_admin = BookAdmin(Book, self.site)

        self.assertEqual(
            model_admin.list_display,
            ("title", "author", "price", "stock", "category", "created_at")
        )
        self.assertEqual(model_admin.list_filter, ("category", "author"))
        self.assertEqual(model_admin.search_fields, ("title", "author"))
        self.assertEqual(model_admin.prepopulated_fields, {"slug": ("title",)})
        self.assertEqual(model_admin.list_editable, ("price", "stock"))

    # -------------------------------------------------------------
    # CART ITEM ADMIN TESTS
    # -------------------------------------------------------------
    def test_cartitem_admin_config(self):
        model_admin = CartItemAdmin(CartItem, self.site)

        self.assertEqual(model_admin.list_display, ("user", "book", "quantity"))
        self.assertEqual(model_admin.search_fields, ("user__username", "book__title"))

    # -------------------------------------------------------------
    # ORDER INLINE TESTS
    # -------------------------------------------------------------
    def test_orderitem_inline_config(self):
        inline = OrderItemInline(OrderItem, self.site)

        self.assertEqual(inline.model, OrderItem)
        self.assertEqual(inline.extra, 0)

    # -------------------------------------------------------------
    # ORDER ADMIN TESTS
    # -------------------------------------------------------------
    def test_order_admin_config(self):
        model_admin = OrderAdmin(Order, self.site)

        self.assertEqual(
            model_admin.list_display,
            ("id", "user", "total_amount", "status", "created_at")
        )
        self.assertEqual(model_admin.list_filter, ("status", "created_at"))
