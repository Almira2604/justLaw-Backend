from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Book, Cart, CartItem


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'profile'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'profile': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
            profile=validated_data.get('profile', None)
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["email"],
            password=data["password"]
        )

        if user and user.is_active:
            return {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }

        raise serializers.ValidationError("Invalid Email or Password")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    # Full book information for the frontend
    book_details = BookSerializer(source='book', read_only=True)

    # Total price for this particular cart item
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'book',
            'book_details',
            'quantity',
            'total'
        ]

    def get_total(self, obj):
        return obj.book.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'datecreated',
            'items'
        ]