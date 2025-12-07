from django.urls import path
from .views import login_view, logout_view,signup_view,home_view,add_to_cart,cart_view,checkout_view, update_cart_item,remove_cart_item,checkout_success_view,address_list,add_address,edit_address,delete_address,order_detail,download_invoice,my_orders_view,book_list_view

"""
All the URL used in Ebook application like login, logout etc
"""

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path("home/", home_view, name="home"),
    path("add-to-cart/<int:book_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", cart_view, name="cart"),
    path("cart/update/<int:item_id>/", update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", remove_cart_item, name="remove_cart_item"),
    path("checkout/", checkout_view, name="checkout"),
    path("checkout/success/<int:order_id>/", checkout_success_view, name="checkout_success"),
    path("addresses/", address_list, name="address_list"),
    path("addresses/add/", add_address, name="add_address"),
    path("addresses/edit/<int:id>/", edit_address, name="edit_address"),
    path("addresses/delete/<int:id>/", delete_address, name="delete_address"),
    path("orders/<int:order_id>/", order_detail, name="order_detail"),
    path("orders/<int:order_id>/invoice/", download_invoice, name="download_invoice"),
    path("orders/", my_orders_view, name="my_orders"),
    path('booklist/', book_list_view, name='booklist'),

    

]