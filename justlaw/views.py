from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Book, Cart, CartItem, User
from .serializer import (
    BookSerializer,
    UserSerializer,
    LoginSerializer,
    CartSerializer,
    CartItemSerializer
)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.get("id"),
                "email": user.get("email"),
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", "")
            }
        }, status=status.HTTP_200_OK)

    errors = serializer.errors

    if "non_field_errors" in errors:
        error_msg = errors["non_field_errors"][0]
    else:
        field = next(iter(errors))

        if isinstance(errors[field], list):
            error_msg = f"{field}: {errors[field][0]}"
        else:
            error_msg = f"{field}: {errors[field]}"

    return Response(
        {
            "error": error_msg,
            "details": errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def signup(request):
    try:
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "message": "Account created successfully",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        errors = serializer.errors

        if "email" in errors:
            error_msg = "A user with this email already exists."
        else:
            field = next(iter(errors))

            if isinstance(errors[field], list):
                error_msg = f"{field}: {errors[field][0]}"
            else:
                error_msg = f"{field}: {errors[field]}"

        return Response(
            {
                "error": error_msg,
                "details": errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================
# BOOKS
# ============================================================

@api_view(['GET', 'POST'])
def book_list_create(request):

    if request.method == 'GET':
        books = Book.objects.all()

        category = request.query_params.get('category')

        if category:
            clean_category = (
                category
                .replace('-', ' ')
                .replace('_', ' ')
            )

            books = books.filter(
                Q(category__iexact=category) |
                Q(category__icontains=clean_category)
            )

        serializer = BookSerializer(books, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    elif request.method == 'POST':

        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "error": "Failed to add book",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, id):

    try:
        book = Book.objects.get(id=id)

    except Book.DoesNotExist:
        return Response(
            {"error": "Book not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':

        serializer = BookSerializer(book)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    elif request.method == 'PUT':

        serializer = BookSerializer(
            book,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "error": "Failed to update book",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == 'DELETE':

        book.delete()

        return Response(
            {"message": "Book deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# ============================================================
# CART
# ============================================================

@api_view(['GET', 'POST'])
def cart_list_create(request):

    # --------------------------------------------------------
    # GET CART
    # --------------------------------------------------------
    if request.method == 'GET':

        user_id = request.query_params.get('user')

        if not user_id:
            return Response(
                {"error": "User parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the user's cart
            cart = Cart.objects.filter(
                user_id=user_id
            ).first()

            # User has no cart yet
            if not cart:
                return Response(
                    [],
                    status=status.HTTP_200_OK
                )

            # Get all items belonging to this cart
            cart_items = CartItem.objects.filter(
                cart=cart
            ).select_related('book')

            serializer = CartItemSerializer(
                cart_items,
                many=True
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {
                    "error": f"Error loading cart: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --------------------------------------------------------
    # ADD TO CART
    # --------------------------------------------------------
    elif request.method == 'POST':

        user_id = request.data.get('user')
        book_id = request.data.get('book')

        try:
            quantity = int(
                request.data.get('quantity', 1)
            )
        except (TypeError, ValueError):
            quantity = 1

        if not user_id:
            return Response(
                {"error": "User is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not book_id:
            return Response(
                {"error": "Book is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check user
        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check book
        try:
            book = Book.objects.get(id=book_id)

        except Book.DoesNotExist:
            return Response(
                {"error": "Book not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(
            user=user
        )

        # Check if this book is already in the cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            book=book,
            defaults={
                'quantity': quantity
            }
        )

        # If already exists, increase quantity
        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)

        return Response(
            serializer.data,
            status=(
                status.HTTP_201_CREATED
                if item_created
                else status.HTTP_200_OK
            )
        )


# ============================================================
# CART ITEM DETAIL
# ============================================================

@api_view(['PUT', 'DELETE'])
def cart_detail(request, id):

    try:
        cart_item = CartItem.objects.select_related(
            'book',
            'cart'
        ).get(id=id)

    except CartItem.DoesNotExist:
        return Response(
            {"error": "Cart item not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # --------------------------------------------------------
    # UPDATE QUANTITY
    # --------------------------------------------------------
    if request.method == 'PUT':

        quantity = request.data.get('quantity')

        if quantity is None:
            return Response(
                {"error": "Quantity is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)

        except (TypeError, ValueError):
            return Response(
                {"error": "Quantity must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # --------------------------------------------------------
    # DELETE CART ITEM
    # --------------------------------------------------------
    elif request.method == 'DELETE':

        cart_item.delete()

        return Response(
            {"message": "Item removed from cart"},
            status=status.HTTP_204_NO_CONTENT
        )