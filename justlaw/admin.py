from django.contrib import admin
from .models import User, Book, Cart, CartItem


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff'
    )
    search_fields = (
        'email',
        'first_name',
        'last_name'
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'category',
        'price',
        'created_at'
    )
    search_fields = (
        'title',
        'author'
    )
    list_filter = (
        'category',
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'datecreated'
    )
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name'
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cart',
        'book',
        'quantity'
    )
    search_fields = (
        'book__title',
        'cart__user__email'
    )