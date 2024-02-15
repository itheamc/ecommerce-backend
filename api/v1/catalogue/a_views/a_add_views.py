from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from catalogue.models import Product, ProductPrice, ProductStock, Attribute, VariationAttribute, \
    ProductAttribute, Brand, VariationAttributeValue, ProductImage, ProductReview, ProductReviewImage
from common.literals import *
from common.response import NetworkResponse
from store.models import StoreStaff


# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------[POST METHODS]----------------------------------------------
# All the views related to POST method for catalog management are defined below
# -----------------------------------------------------------------------------------------------------------


# -----------------------------------@mit-----------------------------------
# Views for adding a base product
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_product(request):
    try:

        # Extract the user from the request
        user = request.user

        # If user is not active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message=ACCOUNT_NOT_ACTIVATED,
                message_code="ACCOUNT_NOT_ACTIVATED",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # If user is not super admin or store admin or store staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the store id from the request
        store_id = request.data.get('store_id')

        # If store id is not provided
        if not store_id:
            return NetworkResponse.get_json_response(
                message_code="STORE_ID_REQUIRED",
                message=STORE_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # If user is staff
        if user.is_staff:
            store_staff = StoreStaff.objects.get(user=user)

            # If store id is not same as the store id of the store staff
            if not store_staff.store_id == store_id:
                return NetworkResponse.get_json_response(
                    message_code="UNAUTHORIZED_TO_ACCESS_OR_MODIFY_ANOTHER_STORE_RESOURCE",
                    message=UNAUTHORIZED_TO_ACCESS_OR_MODIFY_ANOTHER_STORE_RESOURCE,
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Extract base parameter from the request
        is_base = request.query_params.get('is_base')
        is_base = True if is_base == 'true' else False

        # Extract the product data from the request
        product_data = request.data.get('product')

        # If product data is not provided
        if not product_data:
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_DATA_REQUIRED",
                message=PRODUCT_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product name is provided
        if not product_data.get('name'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_NAME_REQUIRED",
                message=PRODUCT_NAME_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if sku is provided
        if not product_data.get('sku'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_SKU_REQUIRED",
                message=PRODUCT_SKU_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product category is provided
        if not product_data.get('category'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_CATEGORY_REQUIRED",
                message=PRODUCT_CATEGORY_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product brand is provided
        if not product_data.get('brand'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_BRAND_REQUIRED",
                message=PRODUCT_BRAND_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product selling price is provided
        if not is_base and not product_data.get('selling_price'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_SELLING_PRICE_REQUIRED",
                message=PRODUCT_SELLING_PRICE_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product mrp is provided
        if not is_base and not product_data.get('mrp'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_MRP_REQUIRED",
                message=PRODUCT_MRP_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product parent is provided
        if not is_base and not product_data.get('parent'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_PARENT_REQUIRED",
                message=PRODUCT_PARENT_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product variation attribute value is provided
        if not is_base and not product_data.get('variation_attribute_value'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_VARIATION_ATTRIBUTE_VALUE_REQUIRED",
                message=PRODUCT_VARIATION_ATTRIBUTE_VALUE_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product quantity is provided
        if not is_base and not product_data.get('quantity'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_QUANTITY_REQUIRED",
                message=PRODUCT_QUANTITY_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extracting parent, category, brand, variation_attribute_value, selling price and mrp from the product data
        parent = product_data.pop('parent') if 'parent' in product_data else None
        category = product_data.pop('category')
        brand = product_data.pop('brand')
        variation_attribute_value = product_data.pop(
            'variation_attribute_value') if 'variation_attribute_value' in product_data else None

        selling_price = product_data.pop('selling_price') if 'selling_price' in product_data else None
        mrp = product_data.pop('mrp') if 'mrp' in product_data else None
        quantity = product_data.pop('quantity') if 'quantity' in product_data else None

        # Create a product object
        product = Product.objects.create(store_id=store_id, parent_id=parent, category_id=category, brand_id=brand,
                                         variation_attribute_value_id=variation_attribute_value, **product_data)

        # Create a product price object if product is not base
        if selling_price and mrp:
            ProductPrice.objects.create(product=product, sp=selling_price, mrp=mrp)

        # Create a product quantity object
        if quantity:
            ProductStock.objects.create(product=product, quantity=quantity, remarks='Initial Stock')

        # return the product object
        return NetworkResponse.get_json_response(
            message_code='PRODUCT_ADDED_SUCCESSFULLY',
            message=PRODUCT_ADDED_SUCCESSFULLY,
            data=product.as_dict_base if is_base else product.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If Store Staff is not found
    except StoreStaff.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="STORE_STAFF_NOT_FOUND",
            message=STORE_STAFF_NOT_FOUND,
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
# Views for adding brand
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_brand(request):
    try:

        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin or store_admin or store_staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the brand data from the request
        brand_data = request.data

        # If brand data is not provided
        if not brand_data:
            return NetworkResponse.get_json_response(
                message_code="BRAND_DATA_REQUIRED",
                message=BRAND_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if brand name is provided
        if not brand_data.get('name') or not brand_data.get('name').strip():
            return NetworkResponse.get_json_response(
                message_code="BRAND_NAME_REQUIRED",
                message=BRAND_NAME_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if category is provided
        if not brand_data.get('category'):
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_ID_REQUIRED",
                message=CATEGORY_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Popping category and store from the brand data
        category = brand_data.pop('category')
        store_id = brand_data.pop('store') if 'store' in brand_data else None

        # Checking if category is list
        if isinstance(category, list):
            brands_list = []

            # Looping through the category list
            for category_id in category:
                # Check if brand exist with same name and category
                if Brand.objects.filter(name__icontains=brand_data.get('name'), category_id=category_id).exists():
                    continue

                # Create a brand object
                brand = Brand.objects.create(store_id=store_id, category_id=category_id,
                                             **brand_data) if store_id else Brand.objects.create(
                    category_id=category_id,
                    **brand_data)

                # Append the brand object to the list
                brands_list.append(brand.as_dict)

            # If no brand is created
            if not brands_list:
                return NetworkResponse.get_json_response(
                    message_code="BRAND_ALREADY_EXISTS",
                    message=BRAND_ALREADY_EXISTS,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Return the brand list
            return NetworkResponse.get_json_response(
                message_code="BRAND_ADDED_SUCCESSFULLY",
                message=BRAND_ADDED_SUCCESSFULLY,
                data=brands_list,
                status=status.HTTP_201_CREATED
            )

        # If category is not list
        # Check if brand exist with same name and category
        if Brand.objects.filter(name__icontains=brand_data.get('name'), category_id=category).exists():
            return NetworkResponse.get_json_response(
                message_code="BRAND_ALREADY_EXISTS",
                message=BRAND_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a brand object
        brand = Brand.objects.create(store_id=store_id, category_id=category,
                                     **brand_data) if store_id else Brand.objects.create(category_id=category,
                                                                                         **brand_data)

        # return the brand object
        return NetworkResponse.get_json_response(
            message_code='BRAND_ADDED_SUCCESSFULLY',
            message=BRAND_ADDED_SUCCESSFULLY,
            data=brand.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding attribute
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_attribute(request):
    try:

        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin
        if not user.is_super_admin:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the attribute data from the request
        attribute_data = request.data

        # If attribute data is not provided
        if not attribute_data:
            return NetworkResponse.get_json_response(
                message_code="ATTRIBUTE_DATA_REQUIRED",
                message=ATTRIBUTE_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if attribute name is provided
        if not attribute_data.get('name') or not attribute_data.get('name').strip():
            return NetworkResponse.get_json_response(
                message_code="ATTRIBUTE_NAME_REQUIRED",
                message=ATTRIBUTE_NAME_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if category is provided
        if not attribute_data.get('category'):
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_ID_REQUIRED",
                message=CATEGORY_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Popping category from the attribute data
        category = attribute_data.pop('category')

        # if category is list
        if isinstance(category, list):

            attributes_list = []

            for category_id in category:
                # Check if attribute exist with same name and category
                if Attribute.objects.filter(name__icontains=attribute_data.get('name'),
                                            category_id=category_id).exists():
                    continue

                # Create a attribute object
                attribute = Attribute.objects.create(category_id=category_id, **attribute_data)
                attributes_list.append(attribute.as_dict)

            # If no attribute is created
            if not attributes_list:
                return NetworkResponse.get_json_response(
                    message_code="ATTRIBUTE_ALREADY_EXISTS",
                    message=ATTRIBUTE_ALREADY_EXISTS,
                    status=status.HTTP_400_BAD_REQUEST
                )

            return NetworkResponse.get_json_response(
                message_code='ATTRIBUTE_ADDED_SUCCESSFULLY',
                message=ATTRIBUTE_ADDED_SUCCESSFULLY,
                data=attributes_list,
                status=status.HTTP_201_CREATED
            )

        # If category is not list
        # Check if attribute exist with same name and category
        if Attribute.objects.filter(name__icontains=attribute_data.get('name'), category_id=category).exists():
            return NetworkResponse.get_json_response(
                message_code="ATTRIBUTE_ALREADY_EXISTS",
                message=ATTRIBUTE_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a attribute object
        attribute = Attribute.objects.create(category_id=category, **attribute_data)

        # return the attribute object
        return NetworkResponse.get_json_response(
            message_code='ATTRIBUTE_ADDED_SUCCESSFULLY',
            message=ATTRIBUTE_ADDED_SUCCESSFULLY,
            data=attribute.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding variation attribute
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_variation_attribute(request):
    try:

        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin
        if not user.is_super_admin:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the variation attribute data from the request
        variation_attribute_data = request.data

        # If variation attribute data is not provided
        if not variation_attribute_data:
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_DATA_REQUIRED",
                message=VARIATION_ATTRIBUTE_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if variation attribute name is provided
        if not variation_attribute_data.get('name') or not variation_attribute_data.get('name').strip():
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_NAME_REQUIRED",
                message=VARIATION_ATTRIBUTE_NAME_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if variation attribute category is provided
        if not variation_attribute_data.get('category'):
            return NetworkResponse.get_json_response(
                message_code="CATEGORY_ID_REQUIRED",
                message=CATEGORY_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Popping category from the variation attribute data
        category = variation_attribute_data.pop('category')

        # if category is list
        if isinstance(category, list):

            variation_attributes_list = []

            for category_id in category:
                # Check if variation attribute exist with same name and category
                if VariationAttribute.objects.filter(name__icontains=variation_attribute_data.get('name'),
                                                     category_id=category_id).exists():
                    continue

                # Create a variation attribute object
                variation_attribute = VariationAttribute.objects.create(category_id=category_id,
                                                                        **variation_attribute_data)
                variation_attributes_list.append(variation_attribute.as_dict)

            # If no variation attribute is created
            if not variation_attributes_list:
                return NetworkResponse.get_json_response(
                    message_code="VARIATION_ATTRIBUTE_ALREADY_EXISTS",
                    message=VARIATION_ATTRIBUTE_ALREADY_EXISTS,
                    status=status.HTTP_400_BAD_REQUEST
                )

            return NetworkResponse.get_json_response(
                message_code='VARIATION_ATTRIBUTE_ADDED_SUCCESSFULLY',
                message=VARIATION_ATTRIBUTE_ADDED_SUCCESSFULLY,
                data=variation_attributes_list,
                status=status.HTTP_201_CREATED
            )

        # If category is not list
        # Check if variation attribute exist with same name and category
        if VariationAttribute.objects.filter(name__icontains=variation_attribute_data.get('name'),
                                             category_id=category).exists():
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_ALREADY_EXISTS",
                message=VARIATION_ATTRIBUTE_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a variation attribute object
        variation_attribute = VariationAttribute.objects.create(category_id=category, **variation_attribute_data)

        # return the variation attribute object
        return NetworkResponse.get_json_response(
            message_code='VARIATION_ATTRIBUTE_ADDED_SUCCESSFULLY',
            message=VARIATION_ATTRIBUTE_ADDED_SUCCESSFULLY,
            data=variation_attribute.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding variation attribute value
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_variation_attribute_value(request):
    try:

        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin or store_admin or store_staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the variation attribute value data from the request
        variation_attribute_value_data = request.data

        # If variation attribute value data is not provided
        if not variation_attribute_value_data:
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_VALUE_DATA_REQUIRED",
                message=VARIATION_ATTRIBUTE_VALUE_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if variation attribute value is provided
        if not variation_attribute_value_data.get('value') or not variation_attribute_value_data.get('value').strip():
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_VALUE_REQUIRED",
                message=VARIATION_ATTRIBUTE_VALUE_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if variation attribute is provided
        if not variation_attribute_value_data.get('variation_attribute'):
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_ID_REQUIRED",
                message=VARIATION_ATTRIBUTE_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # If everything is fine
        # Popping variation attribute and value from the variation attribute value data
        variation_attribute_id = variation_attribute_value_data.pop('variation_attribute')
        value = variation_attribute_value_data.pop('value')

        # Check if variation attribute exist with same value and variation attribute
        if VariationAttributeValue.objects.filter(variation_attribute_id=variation_attribute_id,
                                                  value__icontains=value).exists():
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_VALUE_ALREADY_EXISTS",
                message=VARIATION_ATTRIBUTE_VALUE_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a variation attribute value object
        variation_attribute_value = VariationAttributeValue.objects.create(
            variation_attribute_id=variation_attribute_id, value=value)

        # return the variation attribute value object
        return NetworkResponse.get_json_response(
            message_code='VARIATION_ATTRIBUTE_VALUE_ADDED_SUCCESSFULLY',
            message=VARIATION_ATTRIBUTE_VALUE_ADDED_SUCCESSFULLY,
            data=variation_attribute_value.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding product attribute
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_product_attribute(request):
    try:

        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin or store_admin or store_staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the product attribute data from the request
        product_attribute_data = request.data

        # If product attribute data is not provided
        if not product_attribute_data:
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ATTRIBUTE_DATA_REQUIRED",
                message=PRODUCT_ATTRIBUTE_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product attribute value is provided
        if not product_attribute_data.get('value') or not product_attribute_data.get('value').strip():
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ATTRIBUTE_VALUE_REQUIRED",
                message=PRODUCT_ATTRIBUTE_VALUE_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if attribute is provided
        if not product_attribute_data.get('attribute'):
            return NetworkResponse.get_json_response(
                message_code="ATTRIBUTE_ID_REQUIRED",
                message=ATTRIBUTE_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product is provided
        if not product_attribute_data.get('product'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ID_REQUIRED",
                message=PRODUCT_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Popping attribute, product, and value from the product attribute data
        attribute_id = product_attribute_data.pop('attribute')
        product_id = product_attribute_data.pop('product')
        value = product_attribute_data.pop('value')

        # Check if product attribute exist with same value and attribute
        if ProductAttribute.objects.filter(attribute_id=attribute_id, product_id=product_id).exists():
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ATTRIBUTE_ALREADY_EXISTS",
                message=PRODUCT_ATTRIBUTE_ALREADY_EXISTS,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a product attribute object
        product_attribute = ProductAttribute.objects.create(attribute_id=attribute_id, product_id=product_id,
                                                            value=value)

        # return the product attribute object
        return NetworkResponse.get_json_response(
            message_code='PRODUCT_ATTRIBUTE_ADDED_SUCCESSFULLY',
            message=PRODUCT_ATTRIBUTE_ADDED_SUCCESSFULLY,
            data=product_attribute.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding product price
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_product_price(request):
    try:

        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin or store_admin or store_staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the product price data from the request
        product_price_data = request.data

        # If product price data is not provided
        if not product_price_data:
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_PRICE_DATA_REQUIRED",
                message=PRODUCT_PRICE_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product is provided
        if not product_price_data.get('product'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ID_REQUIRED",
                message=PRODUCT_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if sp is provided
        if not product_price_data.get('sp'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_SELLING_PRICE_REQUIRED",
                message=PRODUCT_SELLING_PRICE_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if mrp is provided
        if not product_price_data.get('mrp'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_MRP_PRICE_REQUIRED",
                message=PRODUCT_MRP_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # If everything is fine, popping product, sp and mrp from the product price data
        product_id = product_price_data.pop('product')
        sp = product_price_data.pop('sp')
        mrp = product_price_data.pop('mrp')

        # Create a product price object
        product_price = ProductPrice.objects.create(product_id=product_id, sp=sp, mrp=mrp)

        # return the product price object
        return NetworkResponse.get_json_response(
            message_code='PRODUCT_PRICE_ADDED_SUCCESSFULLY',
            message=PRODUCT_PRICE_ADDED_SUCCESSFULLY,
            data=product_price.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding product stock
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_product_stock(request):
    try:

        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin or store_admin or store_staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the product stock data from the request
        product_stock_data = request.data

        # If product stock data is not provided
        if not product_stock_data:
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_STOCK_DATA_REQUIRED",
                message=PRODUCT_STOCK_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product is provided
        if not product_stock_data.get('product'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ID_REQUIRED",
                message=PRODUCT_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if quantity is provided
        if not product_stock_data.get('quantity'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_QUANTITY_REQUIRED",
                message=PRODUCT_QUANTITY_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # If everything is fine, popping product and quantity from the product stock data
        product_id = product_stock_data.pop('product')
        quantity = product_stock_data.pop('quantity')

        # Create a product stock object
        product_stock = ProductStock.objects.create(product_id=product_id, quantity=quantity, **product_stock_data)

        # return the product stock object
        return NetworkResponse.get_json_response(
            message_code='PRODUCT_STOCK_ADDED_SUCCESSFULLY',
            message=PRODUCT_STOCK_ADDED_SUCCESSFULLY,
            data=product_stock.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding product image
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser])
def add_product_image(request):
    try:
        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin or store_admin or store_staff
        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the product image data from the request
        product_image_data = request.data

        # If product image data is not provided
        if not product_image_data:
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_IMAGE_DATA_REQUIRED",
                message=PRODUCT_IMAGE_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product is provided
        if not product_image_data.get('product'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ID_REQUIRED",
                message=PRODUCT_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if image is provided
        if not product_image_data.get('image'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_IMAGE_REQUIRED",
                message=PRODUCT_IMAGE_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # If everything is fine, popping product and image from the product image data
        product_id = product_image_data.get('product')
        if isinstance(product_image_data.get('product'), str):
            product_id = int(product_id)
        image = product_image_data.get('image')

        # Create a product image object
        product_image = ProductImage.objects.create(product_id=product_id, image=image)

        # return the product image object
        return NetworkResponse.get_json_response(
            message_code='PRODUCT_IMAGE_ADDED_SUCCESSFULLY',
            message=PRODUCT_IMAGE_ADDED_SUCCESSFULLY,
            data=product_image.as_dict,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for adding product review
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser])
def add_product_review(request):
    try:
        # Extract user from the request
        user = request.user

        # Check if user is active
        if not user.is_active:
            return NetworkResponse.get_json_response(
                message_code="ACCOUNT_NOT_ACTIVATED",
                message=ACCOUNT_NOT_ACTIVATED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is super_admin or store_admin or store_staff
        if user.is_super_admin or user.is_store_admin or user.is_staff:
            return NetworkResponse.get_json_response(
                message_code="ACCESS_DENIED",
                message=ACCESS_DENIED,
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract the product review data from the request
        product_review_data = request.data

        # Extracting images from the request
        images = request.FILES.getlist('images')
        print(images)

        # If product review data is not provided
        if not product_review_data:
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_REVIEW_DATA_REQUIRED",
                message=PRODUCT_REVIEW_DATA_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if product is provided
        if not product_review_data.get('product'):
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ID_REQUIRED",
                message=PRODUCT_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if customer is provided
        if not product_review_data.get('customer'):
            return NetworkResponse.get_json_response(
                message_code="CUSTOMER_ID_REQUIRED",
                message=CUSTOMER_ID_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if rating is provided
        if not product_review_data.get('rating'):
            return NetworkResponse.get_json_response(
                message_code="RATING_REQUIRED",
                message=RATING_REQUIRED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # If everything is fine getting product and customer from the product review data
        product_id = product_review_data.get('product')
        if isinstance(product_review_data.get('product'), str):
            product_id = int(product_id)

        customer_id = product_review_data.get('customer')
        if isinstance(product_review_data.get('customer'), str):
            customer_id = int(customer_id)

        rating = product_review_data.get('rating')
        if isinstance(product_review_data.get('rating'), str):
            rating = float(rating)

        comment = product_review_data.get('comment') if product_review_data.get('comment') else None

        # If review is already added for the product
        if ProductReview.objects.filter(product_id=product_id, customer_id=customer_id).exists():
            return NetworkResponse.get_json_response(
                message_code="REVIEW_ALREADY_ADDED",
                message=REVIEW_ALREADY_ADDED,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a product review object
        product_review = ProductReview.objects.create(product_id=product_id, customer_id=customer_id, rating=rating,
                                                      comment=comment)

        # If images are provided, add them to the product review
        if images:
            for image in images:
                ProductReviewImage.objects.create(review_id=product_review.id, image=image)

        # return the product review object
        return NetworkResponse.get_json_response(
            message_code='PRODUCT_REVIEW_ADDED_SUCCESSFULLY',
            message=PRODUCT_REVIEW_ADDED_SUCCESSFULLY,
            data=product_review.as_dict_min,
            status=status.HTTP_201_CREATED
        )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
