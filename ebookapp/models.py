from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Every book belongs to Category 
    Category have name and slug
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        """
        to achieve reordering as per name
        plural form is categories
        """
        ordering = ["name"]
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return str(self.name)


class Book(models.Model):
    """
    Core model of application with all the params

    """
    title = models.CharField(max_length=20)
    author = models.CharField(max_length=20)
    description = models.TextField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to="books/", blank=True, null=True)


    class Meta:
        """
        ordering through title
        """
        ordering = ["title"]

    def __str__(self):
        """
        to get title on dashboard
        """
        return f"{self.title} by {self.author}"


class CartItem(models.Model):
    """
    To manage the cart item which acts as a bridge between user and books
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ["user","book"]
    
    def total_price(self):
     """
     This function will help to get total price as per quantity of a item
     """
     return self.book.price * self.quantity  # pylint: disable=no-member
    
    def __str__(self):
        return f"{self.book.title} x {self.quantity}" # pylint: disable=no-member
    


class Order(models.Model):
    """
    To track users order 
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey("Address", on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"  # pylint: disable=no-member

    

class OrderItem(models.Model):
    """
    To track all items in a order
    """
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}" # pylint: disable=no-member
    

class Address(models.Model):
    """
    To manage address for user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=30, default="India")

    def __str__(self):
        return f"{self.full_name} - {self.city}"