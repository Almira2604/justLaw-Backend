from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
from django.conf import settings


class Book(models.Model):
    LAW_CATEGORIES = [
        ('criminal', 'Criminal Law'),
        ('constitutional', 'Constitutional Law'),
        ('corporate', 'Corporate Law'),
        ('property', 'Property Law'),
        ('administrative', 'Administrative Law'),
        ('contract', 'Contract Law'),
        ('family', 'Family Law'),
        ('tax', 'Tax Law'),
        ('intellectual_property', 'Intellectual Property Law'),
        ('environmental', 'Environmental Law'),
    ]

    title = models.CharField(max_length=200)    
    author = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=LAW_CATEGORIES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='law_books/covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    profile = models.ImageField(upload_to="profile")
    last_login = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "password"]


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datecreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user.first_name}"


# Standalone class (outdented from Cart)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"