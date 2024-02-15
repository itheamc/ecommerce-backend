from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from common.response import NetworkResponse
from common.models import *
from common.literals import *


# -------------------------------@mit--------------------------------
# Method to get store categories - main or sub-categories
@api_view(['GET'])
def get_store_categories(request):
    try:
        # Extracting the category id from the request
        category_id = request.GET.get('category')

        # If category id is none
        if category_id is None:
            # Filtering main store categories
            categories = Category.objects.filter(parent=None, is_active=True)

            categories_res = [category.as_dict_min for category in categories]
            return NetworkResponse.get_json_response(
                message_code="STORE_CATEGORIES_RETRIEVED",
                message=STORE_CATEGORIES_RETRIEVED,
                data=categories_res,
                status=status.HTTP_200_OK)

        # Filtering the store sub categories
        # With a condition that the store sub category is active and parent's parent category is null
        sub_categories = Category.objects.filter(parent_id=category_id, is_active=True, parent__is_active=True)

        # If sub categories are found
        # Creating a dictionary for each sub category
        sub_categories_res = [sub_category.as_dict_min for sub_category in sub_categories]
        return NetworkResponse.get_json_response(
            message_code="STORE_SUB_CATEGORIES_RETRIEVED",
            message=STORE_SUB_CATEGORIES_RETRIEVED,
            data=sub_categories_res,
            status=status.HTTP_200_OK)
    # If any error occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------@mit--------------------------------
# Method to get product categories - as per store category
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_categories(request):
    try:

        # Extracting the user from the request
        user = request.user

        # Checking if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_401_UNAUTHORIZED)

        # If user is not a store admin or staff or super admin
        if not user.is_store_admin and not user.is_staff and not user.is_superuser:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extracting the store category id from the request
        store_category_id = request.GET.get('category')

        # If store category id is none
        if store_category_id is None:
            return NetworkResponse.get_json_response(
                message_code="STORE_CATEGORY_ID_REQUIRED",
                message=STORE_CATEGORY_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtering the product categories with given store category id
        product_categories = Category.objects.filter(parent_id=store_category_id, is_active=True,
                                                     parent__is_active=True)
        # Creating a dictionary for each product category
        product_categories_res = [product_c.as_dict_min for product_c in product_categories]
        return NetworkResponse.get_json_response(
            message_code="PRODUCT_CATEGORIES_RETRIEVED",
            message=PRODUCT_CATEGORIES_RETRIEVED,
            data=product_categories_res,
            status=status.HTTP_200_OK
        )

    # If any error occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------@mit--------------------------------
# Method to get category by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_category(request, category_id):
    try:
        # Get the user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if the user is a store admin or super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Filtering the category with given category id
        category = Category.objects.get(id=category_id)

        # If category is found
        # Creating a dictionary for the category
        category_res = category.as_dict_min

        return NetworkResponse.get_json_response(
            message_code="CATEGORY_RETRIEVED",
            message=CATEGORY_RETRIEVED,
            data=category_res,
            status=status.HTTP_200_OK)

    # If category is not found
    except Category.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="CATEGORY_NOT_FOUND",
            message=CATEGORY_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any error occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -------------------------------@mit--------------------------------
# Method to add category
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser])
def add_category(request):
    try:
        # Extracting the user from the request
        user = request.user

        # Checking if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Checking if the user is a staff or store admin or super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extracting the category data from the request
        category_data = request.data

        # Checking if the category data is none
        if category_data is None:
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_DATA_REQUIRED",
                message=CATEGORY_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extracting the category name from the request
        category_name = category_data.get('name') if 'name' in category_data else None

        # Checking if the category name is none
        if category_name is None:
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_NAME_REQUIRED",
                message=CATEGORY_NAME_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Checking if the category name is already exists
        if Category.objects.filter(name__iexact=category_name).exists():
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_NAME_ALREADY_EXISTS",
                message=CATEGORY_NAME_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extracting the category description from the request
        category_description = category_data.get('description') if 'description' in category_data else None

        # Extracting the category image from the request
        category_image = request.FILES.get('image') if 'image' in request.FILES else None

        # Extracting the category parent id from the request
        category_parent_id = category_data.pop('parent') if 'parent' in category_data else None
        if category_parent_id and isinstance(category_parent_id, str):
            category_parent_id = int(category_parent_id)

        # Creating a category object
        category = Category.objects.create(name=category_name, description=category_description, image=category_image,
                                           parent_id=category_parent_id) if category_parent_id else Category.objects.create(
            name=category_name, description=category_description, image=category_image)

        # If category is created
        if category:
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_CREATED_SUCCESSFULLY",
                message=CATEGORY_CREATED_SUCCESSFULLY,
                data=category.as_dict,
                status=status.HTTP_201_CREATED
            )

        # If category is not created
        else:
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_CREATED_FAILED",
                message=CATEGORY_CREATED_FAILED,
                status=status.HTTP_400_BAD_REQUEST
            )

    # If any error occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -------------------------------@mit--------------------------------
# Method to update category
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser])
def update_category(request, category_id):
    try:

        # Extracting the user from the request
        user = request.user

        # Checking if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Checking if the user is a staff or store admin or super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extracting the category data from the request
        category_data = request.data

        # Checking if the category data is none
        if category_data is None:
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_DATA_REQUIRED",
                message=CATEGORY_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extracting the category name from the request
        category_name = category_data.get('name') if 'name' in category_data else None

        # Extracting the category description from the request
        category_description = category_data.get('description') if 'description' in category_data else None

        # Extracting the category image from the request
        category_image = request.FILES.get('image') if 'image' in request.FILES else None

        # Extracting the category parent id from the request
        category_parent_id = category_data.pop('parent') if 'parent' in category_data else None

        # Checking if the category parent id is none
        if category_parent_id and isinstance(category_parent_id, str):
            category_parent_id = int(category_parent_id)

        # Getting the category object
        category = Category.objects.get(id=category_id)

        # Creating variable to check if the category is updated
        is_updated = False

        # Checking if the category name is none
        if category_name and category_name != category.name:
            category.name = category_name
            is_updated = True

        # Checking if the category description is none
        if category_description and category_description != category.description:
            category.description = category_description
            is_updated = True

        # Checking if the category image is none
        if category_image and category_image != category.image:
            category.image = category_image
            is_updated = True

        # Checking if the category parent id is none
        if category_parent_id and category_parent_id != category.parent_id:
            category.parent = Category.objects.get(id=category_parent_id)
            is_updated = True

        # If category is updated
        if is_updated:
            category.save()
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_UPDATED_SUCCESSFULLY",
                message=CATEGORY_UPDATED_SUCCESSFULLY,
                data=category.as_dict,
                status=status.HTTP_200_OK
            )

        # If category is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            data=category.as_dict,
            status=status.HTTP_200_OK
        )

    # If category is not found
    except Category.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="CATEGORY_NOT_FOUND",
            message=CATEGORY_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any error occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
