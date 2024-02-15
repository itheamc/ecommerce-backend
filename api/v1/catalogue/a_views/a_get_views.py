from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from catalogue.models import Product, ProductPrice, ProductStock, Attribute, VariationAttribute, \
    VariationAttributeValue, ProductAttribute, Brand, ProductImage
from common.literals import *
from common.response import NetworkResponse


# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------[GET METHODS]-----------------------------------------------
# All the views related to GET method for catalog management are defined below
# -----------------------------------------------------------------------------------------------------------


# -----------------------------------@mit-----------------------------------
# Views for getting products
# params:
#   - store ~ id of the store
#   - category ~ id of the category
#   - parent ~ id of the parent product
#   - base_only
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_products(request):
    try:

        # Extract the user from the request
        user = request.user

        # Getting the store_id from the request
        store_id = request.GET.get('store')

        # Getting the category_id from the request
        category_id = request.GET.get('category')

        # Getting the parent_id from the request
        parent_id = request.GET.get('parent')

        # Getting the base_only from the request - may be true or false
        base_only = request.GET.get('base_only')
        base_only = True if base_only == 'true' else False

        # If store_id is not provided
        if not store_id:
            return NetworkResponse.get_json_response(
                message_code="STORE_ID_REQUIRED",
                message=STORE_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # If user is super admin or store admin or staff
        if user.is_super_admin or user.is_store_admin or user.is_staff:
            # If parent_id is provided
            if parent_id:
                # Retrieve the product
                products = Product.objects.filter(parent_id=parent_id,
                                                  category_id=category_id,
                                                  store_id=store_id) if category_id else Product.objects.filter(
                    parent_id=parent_id, store_id=store_id)

                products_res = [product.as_dict for product in products]

                return NetworkResponse.get_json_response(
                    message_code="PRODUCT_LIST_RETRIEVED",
                    message=PRODUCT_LIST_RETRIEVED,
                    data=products_res,
                    status=status.HTTP_200_OK
                )

            # If base_only is true
            if base_only:
                # Retrieve the product
                products = Product.objects.filter(parent=None,
                                                  category_id=category_id,
                                                  store_id=store_id) if category_id else Product.objects.filter(
                    parent=None, store_id=store_id)

                products_res = [product.as_dict_base for product in products]

                return NetworkResponse.get_json_response(
                    message_code="PRODUCT_LIST_RETRIEVED",
                    message=PRODUCT_LIST_RETRIEVED,
                    data=products_res,
                    status=status.HTTP_200_OK
                )

            # If Neither parent_id nor base_only is provided
            products = Product.objects.filter(store_id=store_id, parent__isnull=False, parent__parent=None,
                                              category_id=category_id) if category_id else Product.objects.filter(
                store_id=store_id, parent__isnull=False, parent__parent=None)

            products_res = [product.as_dict for product in products]

            return NetworkResponse.get_json_response(
                message_code="PRODUCT_LIST_RETRIEVED",
                message=PRODUCT_LIST_RETRIEVED,
                data=products_res,
                status=status.HTTP_200_OK
            )

        # If user is not super admin or store admin or staff i.e. user is a customer
        # If parent_id is provided
        if parent_id:
            # Retrieve the product
            products = Product.objects.filter(store_id=store_id, parent_id=parent_id,
                                              category_id=category_id, is_active=True,
                                              is_approved=True,
                                              status='published') if category_id else Product.objects.filter(
                store_id=store_id, parent_id=parent_id, is_active=True, is_approved=True, status='published')

            products_res = [product.as_dict_min for product in products]

            return NetworkResponse.get_json_response(
                message_code="PRODUCT_LIST_RETRIEVED",
                message=PRODUCT_LIST_RETRIEVED,
                data=products_res,
                status=status.HTTP_200_OK
            )

        # If base_only is true
        if base_only:
            # Retrieve the product
            products = Product.objects.filter(parent=None,
                                              category_id=category_id,
                                              store_id=store_id, is_active=True,
                                              is_approved=True,
                                              status='published') if category_id else Product.objects.filter(
                parent=None, store_id=store_id, is_active=True, is_approved=True, status='published')

            products_res = [product.as_dict_base_min for product in products]

            return NetworkResponse.get_json_response(
                message_code="PRODUCT_LIST_RETRIEVED",
                message=PRODUCT_LIST_RETRIEVED,
                data=products_res,
                status=status.HTTP_200_OK
            )

        # If Neither parent_id nor base_only is provided
        products = Product.objects.filter(store_id=store_id, parent__isnull=False, parent__parent=None,
                                          category_id=category_id, is_active=True,
                                          is_approved=True,
                                          status='published') if category_id else Product.objects.filter(
            store_id=store_id, parent__isnull=False, parent__parent=None, is_active=True, is_approved=True,
            status='published')

        products_res = [product.as_dict_min for product in products]

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_LIST_RETRIEVED",
            message=PRODUCT_LIST_RETRIEVED,
            data=products_res,
            status=status.HTTP_200_OK
        )

    # If other exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting single product by id
# params:
#   - store ~ id of the store
#   - child ~ boolean to indicate if child should be included
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product(request, product_id):
    # Try to get the product
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

        # Extracting the store id from the request
        store_id = request.query_params.get('store')

        # Extracting the with_child from the request
        with_child = request.query_params.get('child')
        with_child = True if with_child == 'true' else False

        # If user is super admin
        if user.is_super_admin:
            # Retrieve the product
            product = Product.objects.get(id=product_id)

            product_res = product.as_dict if not with_child else product.as_dict_with_child

            return NetworkResponse.get_json_response(
                message_code="PRODUCT_RETRIEVED",
                message=PRODUCT_RETRIEVED,
                data=product_res,
                status=status.HTTP_200_OK
            )

        # If store_id is not provided
        if not store_id:
            return NetworkResponse.get_json_response(
                message=STORE_ID_REQUIRED,
                message_code="STORE_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filtering the product
        products = Product.objects.filter(
            id=product_id, store_id=store_id) if user.is_store_admin or user.is_staff else Product.objects.filter(
            id=product_id, store_id=store_id, is_active=True, is_approved=True, status='published')

        # Getting the first product from the list
        product = products.first() if products.exists() else None

        # If product is not found
        if not product:
            return NetworkResponse.get_json_response(
                message=PRODUCT_NOT_FOUND,
                message_code="PRODUCT_NOT_FOUND",
                status=status.HTTP_404_NOT_FOUND
            )

        product_res = (
            product.as_dict if not with_child else product.as_dict_with_child) if user.is_store_admin or user.is_staff else (
            product.as_dict_min if not with_child else product.as_dict_with_child)

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_RETRIEVED",
            message=PRODUCT_RETRIEVED,
            data=product_res,
            status=status.HTTP_200_OK
        )

    # If product is not found
    except Product.DoesNotExist:
        return NetworkResponse.get_json_response(
            message=PRODUCT_NOT_FOUND,
            message_code="PRODUCT_NOT_FOUND",
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting attributes
# params:
#   - category ~ id of the store category
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_attributes(request):
    # Try to get the attributes
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

        # Extracting the category id from the request
        category_id = request.query_params.get('category')

        # If user is not super admin or store admin or staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # If user is super admin
        if user.is_super_admin:
            # Retrieve the attributes
            attributes = Attribute.objects.filter(category_id=category_id) if category_id else Attribute.objects.all()

            # Generating the response
            attributes_res = [attribute.as_dict for attribute in attributes]

            return NetworkResponse.get_json_response(
                message_code="ATTRIBUTE_LIST_RETRIEVED",
                message=ATTRIBUTE_LIST_RETRIEVED,
                data=attributes_res,
                status=status.HTTP_200_OK
            )

        # If category_id is not provided
        if not category_id:
            return NetworkResponse.get_json_response(
                message=CATEGORY_ID_REQUIRED,
                message_code="CATEGORY_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # If user is store admin or staff
        attributes = Attribute.objects.filter(category_id=category_id)

        # Generating the response
        attributes_res = [attribute.as_dict_min for attribute in attributes]

        return NetworkResponse.get_json_response(
            message_code="ATTRIBUTE_LIST_RETRIEVED",
            message=ATTRIBUTE_LIST_RETRIEVED,
            data=attributes_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting variation attributes
# params:
#   - category ~ id of the store category
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_variation_attributes(request):
    # Try to get the variation attributes
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extracting the category id from the request
        category_id = request.query_params.get('category')

        # If user is not super admin or store admin or staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # If user is super admin
        if user.is_super_admin:
            # Retrieve the variation attributes
            variation_attributes = VariationAttribute.objects.filter(
                category_id=category_id) if category_id else VariationAttribute.objects.all()

            # Generating the response
            variation_attributes_res = [attribute.as_dict for attribute in variation_attributes]

            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_LIST_RETRIEVED",
                message=VARIATION_ATTRIBUTE_LIST_RETRIEVED,
                data=variation_attributes_res,
                status=status.HTTP_200_OK
            )

        # If not a super admin and category_id is not provided
        if not category_id:
            return NetworkResponse.get_json_response(
                message=CATEGORY_ID_REQUIRED,
                message_code="CATEGORY_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # If user is store admin or staff
        variation_attributes = Attribute.objects.filter(category_id=category_id)

        # Generating the response
        variation_attributes_res = [attribute.as_dict_min for attribute in variation_attributes]

        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_LIST_RETRIEVED",
            message=VARIATION_ATTRIBUTE_LIST_RETRIEVED,
            data=variation_attributes_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting variation attribute values
# params:
#   - variation_attribute ~ id of the variation attribute
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_variation_attribute_values(request):
    # Try to get the variation attribute values
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extracting the variation attribute id from the request
        variation_attribute_id = request.query_params.get('variation_attribute')

        # If variation_attribute_id is not provided
        if not variation_attribute_id:
            return NetworkResponse.get_json_response(
                message=VARIATION_ATTRIBUTE_ID_REQUIRED,
                message_code="VARIATION_ATTRIBUTE_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # If user is not super admin or store admin or staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the variation attribute values
        variation_attribute_values = VariationAttributeValue.objects.filter(
            variation_attribute_id=variation_attribute_id)

        # Generating the response
        variation_attribute_values_res = [
            attribute_value.as_dict if user.is_super_admin else attribute_value.as_dict_min for attribute_value in
            variation_attribute_values]

        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_VALUE_LIST_RETRIEVED",
            message=VARIATION_ATTRIBUTE_VALUE_LIST_RETRIEVED,
            data=variation_attribute_values_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting product attributes
# params:
#   - product ~ id of the product
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_attributes(request):
    # Try to get the product attributes
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extracting the product id from the request
        product_id = request.query_params.get('product')

        # If product_id is not provided
        if not product_id:
            return NetworkResponse.get_json_response(
                message=PRODUCT_ID_REQUIRED,
                message_code="PRODUCT_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the product attributes
        product_attributes = ProductAttribute.objects.filter(product_id=product_id)

        # Generating the response
        product_attributes_res = [attribute.as_dict if user.is_super_admin else attribute.as_dict_min for attribute in
                                  product_attributes]

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_ATTRIBUTE_LIST_RETRIEVED",
            message=PRODUCT_ATTRIBUTE_LIST_RETRIEVED,
            data=product_attributes_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting brands
# params:
#   - category ~ id of the store category
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_brands(request):
    # Try to get the brands
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not super admin or store admin or staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Extracting the category id from the request
        category_id = request.query_params.get('category')

        # If category_id is not provided
        if not category_id:
            return NetworkResponse.get_json_response(
                message=CATEGORY_ID_REQUIRED,
                message_code="CATEGORY_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the brands
        brands = Brand.objects.filter(category_id=category_id)

        # Generating the response
        brands_res = [brand.as_dict if user.is_super_admin else brand.as_dict_min for brand in brands]

        return NetworkResponse.get_json_response(
            message_code="BRAND_LIST_RETRIEVED",
            message=BRAND_LIST_RETRIEVED,
            data=brands_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting product prices
# params:
#   - product ~ id of the product
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_prices(request):
    # Try to get the product prices
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not super admin or store admin or staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Extracting the product id from the request
        product_id = request.query_params.get('product')

        # If product_id is not provided
        if not product_id:
            return NetworkResponse.get_json_response(
                message=PRODUCT_ID_REQUIRED,
                message_code="PRODUCT_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the product prices
        product_prices = ProductPrice.objects.filter(product_id=product_id)

        # Generating the response
        product_prices_res = [price.as_dict for price in product_prices]

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_PRICE_LIST_RETRIEVED",
            message=PRODUCT_PRICE_LIST_RETRIEVED,
            data=product_prices_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting product stocks
# params:
#   - product ~ id of the product
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_stocks(request):
    # Try to get the product stocks
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not super admin or store admin or staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Extracting the product id from the request
        product_id = request.query_params.get('product')

        # If product_id is not provided
        if not product_id:
            return NetworkResponse.get_json_response(
                message=PRODUCT_ID_REQUIRED,
                message_code="PRODUCT_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the product stocks
        product_stocks = ProductStock.objects.filter(product_id=product_id)

        # Generating the response
        product_stocks_res = [stock.as_dict for stock in product_stocks]

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_STOCK_LIST_RETRIEVED",
            message=PRODUCT_STOCK_LIST_RETRIEVED,
            data=product_stocks_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting product images
# params:
#   - product ~ id of the product
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_images(request):
    # Try to get the product images
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extracting the product id from the request
        product_id = request.query_params.get('product')

        # If product_id is not provided
        if not product_id:
            return NetworkResponse.get_json_response(
                message=PRODUCT_ID_REQUIRED,
                message_code="PRODUCT_ID_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the product images
        product_images = ProductImage.objects.filter(product_id=product_id)

        # Generating the response
        product_images_res = [image.as_dict_min if not user.is_staff else image.as_dict for image in product_images]

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_IMAGE_LIST_RETRIEVED",
            message=PRODUCT_IMAGE_LIST_RETRIEVED,
            data=product_images_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for searching products with the given query
# params:
#   - query ~ query to search for
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
def search_products(request):
    # Try to search for products
    try:
        # Get the requested user
        # user = request.user

        # Check if the user is active
        # if not user.is_active:
        #     return NetworkResponse.get_json_response(
        #         message=ACCOUNT_NOT_ACTIVATED,
        #         message_code="ACCOUNT_NOT_ACTIVATED",
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )

        # getting the query from the request
        query = request.query_params.get('query')

        # If query is not provided
        if not query:
            return NetworkResponse.get_json_response(
                message=QUERY_REQUIRED,
                message_code="QUERY_REQUIRED",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the products having parent's parent null with the given query
        # matching the query with the product name or tags
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(tags__icontains=query) | Q(description__icontains=query),
            parent__isnull=False
        )

        # Generating the response
        products_res = [product.as_dict_min for product in products]

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_LIST_RETRIEVED",
            message=PRODUCT_LIST_RETRIEVED,
            data=products_res,
            status=status.HTTP_200_OK
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting brand by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_brand(request, brand_id):
    # Try to get the brand
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not staff, not store admin and is not the super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the brand
        brand = Brand.objects.get(id=brand_id)

        # Generating the response
        brand_res = brand.as_dict_details

        return NetworkResponse.get_json_response(
            message_code="BRAND_RETRIEVED",
            message=BRAND_RETRIEVED,
            data=brand_res,
            status=status.HTTP_200_OK
        )

    # If Brand does not exist
    except Brand.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="BRAND_DOES_NOT_EXIST",
            message=BRAND_DOES_NOT_EXIST,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting a attribute by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_attribute(request, attribute_id):
    # Try to get the attribute
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not staff, not store admin and is not the super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the attribute
        attribute = Attribute.objects.get(id=attribute_id)

        # Generating the response
        attribute_res = attribute.as_dict_details

        return NetworkResponse.get_json_response(
            message_code="ATTRIBUTE_RETRIEVED",
            message=ATTRIBUTE_RETRIEVED,
            data=attribute_res,
            status=status.HTTP_200_OK
        )

    # If Attribute does not exist
    except Attribute.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="ATTRIBUTE_DOES_NOT_EXIST",
            message=ATTRIBUTE_DOES_NOT_EXIST,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting a variation attribute by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_variation_attribute(request, variation_attribute_id):
    # Try to get the variation attribute
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not staff, not store admin and is not the super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the variation attribute
        variation_attribute = VariationAttribute.objects.get(id=variation_attribute_id)

        # Generating the response
        variation_attribute_res = variation_attribute.as_dict_details

        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_RETRIEVED",
            message=VARIATION_ATTRIBUTE_RETRIEVED,
            data=variation_attribute_res,
            status=status.HTTP_200_OK
        )

    # If VariationAttribute does not exist
    except VariationAttribute.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_NOT_FOUND",
            message=VARIATION_ATTRIBUTE_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting a variation attribute value by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_variation_attribute_value(request, variation_attribute_value_id):
    # Try to get the variation attribute value
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not staff, not store admin and is not the super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the variation attribute value
        variation_attribute_value = VariationAttributeValue.objects.get(id=variation_attribute_value_id)

        # Generating the response
        variation_attribute_value_res = variation_attribute_value.as_dict_details

        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_VALUE_RETRIEVED",
            message=VARIATION_ATTRIBUTE_VALUE_RETRIEVED,
            data=variation_attribute_value_res,
            status=status.HTTP_200_OK
        )

    # If VariationAttributeValue does not exist
    except VariationAttributeValue.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_VALUE_NOT_FOUND",
            message=VARIATION_ATTRIBUTE_VALUE_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting a product attribute by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_attribute(request, product_attribute_id):
    # Try to get the product attribute
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not staff, not store admin and is not the super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the product attribute
        product_attribute = ProductAttribute.objects.get(id=product_attribute_id)

        # Generating the response
        product_attribute_res = product_attribute.as_dict

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_ATTRIBUTE_RETRIEVED",
            message=PRODUCT_ATTRIBUTE_RETRIEVED,
            data=product_attribute_res,
            status=status.HTTP_200_OK
        )

    # If ProductAttribute does not exist
    except ProductAttribute.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="PRODUCT_ATTRIBUTE_NOT_FOUND",
            message=PRODUCT_ATTRIBUTE_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting a product price by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_price(request, product_price_id):
    # Try to get the product price
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not staff, not store admin and is not the super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the product price
        product_price = ProductPrice.objects.get(id=product_price_id)

        # Generating the response
        product_price_res = product_price.as_dict

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_PRICE_RETRIEVED",
            message=PRODUCT_PRICE_RETRIEVED,
            data=product_price_res,
            status=status.HTTP_200_OK
        )

    # If ProductPrice does not exist
    except ProductPrice.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="PRODUCT_PRICE_NOT_FOUND",
            message=PRODUCT_PRICE_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for getting a product stock by id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_product_stock(request, product_stock_id):
    # Try to get the product stock
    try:
        # Get the requested user
        user = request.user

        # Check if the user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If user is not staff, not store admin and is not the super admin
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message=ACCESS_DENIED,
                message_code="ACCESS_DENIED",
                status=status.HTTP_403_FORBIDDEN
            )

        # Retrieve the product stock
        product_stock = ProductStock.objects.get(id=product_stock_id)

        # Generating the response
        product_stock_res = product_stock.as_dict

        return NetworkResponse.get_json_response(
            message_code="PRODUCT_STOCK_RETRIEVED",
            message=PRODUCT_STOCK_RETRIEVED,
            data=product_stock_res,
            status=status.HTTP_200_OK
        )

    # If ProductStock does not exist
    except ProductStock.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="PRODUCT_STOCK_NOT_FOUND",
            message=PRODUCT_STOCK_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
