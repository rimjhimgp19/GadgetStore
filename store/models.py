




from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone


# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)  # Just use auto_now_add, no need for default
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Calculate subtotal when saving the CartItem
        self.subtotal = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) - {self.user.username}"







class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by {self.user.username} - Total: {self.total}"









class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate the price for each order item (based on quantity and product price)
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - Total: {self.price}" 
    





from django.db import models
from django.contrib.auth.models import User

class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
