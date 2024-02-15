from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from catalogue.models import Product, ProductPrice, ProductStock, Attribute, VariationAttribute, \
    ProductAttribute, Brand, VariationAttributeValue, ProductImage
from common.literals import *
from common.models import Category
from common.response import NetworkResponse

# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------[GET METHODS]-----------------------------------------------
# All the views related to GET method for catalog management are defined below
# -----------------------------------------------------------------------------------------------------------


# -----------------------------------@mit-----------------------------------
# Views for updating the brand
from store.models import Store


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@parser_classes([MultiPartParser])
def update_brand(request, brand_id):
    try:

        # Extracting the user from the request
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

        # Extracting the brand data from the request
        brand_data = request.data

        # popping all the expected keys from the request data
        name = brand_data.get('name', None)
        description = brand_data.get('description', None)
        category = brand_data.get('category', None)
        if isinstance(category, str):
            category = int(category)

        store = brand_data.get('store', None)
        if isinstance(store, str):
            store = int(store)

        is_active = brand_data.get('is_active', None)

        image = brand_data.get('image', None)

        # Getting the brand from the database
        brand = Brand.objects.get(id=brand_id)

        # variable to check if the brand is updated or not
        is_updated = False

        # Updating the brand
        # if name and name != brand.name
        if name and name != brand.name:
            brand.name = name
            is_updated = True
        # if description and description != brand.description
        if description and description != brand.description:
            brand.description = description
            is_updated = True
        # if category and category != brand.category.id
        if category and category != brand.category.id:
            brand.category = Category.objects.get(id=category)
            is_updated = True
        # if store and store != brand.store.id
        if store and store != brand.store.id:
            brand.store = Store.objects.get(id=store)
            is_updated = True
        # if is_active and is_active != brand.is_active
        if is_active:
            is_active = True if is_active == 'true' else False
            if is_active != brand.is_active:
                brand.is_active = is_active
                is_updated = True
        # if image:
        if image:
            brand.image = image
            is_updated = True

        # if the brand is updated
        if is_updated:
            # Saving the brand
            brand.save()

            # Returning the response
            return NetworkResponse.get_json_response(
                message_code="BRAND_UPDATED_SUCCESSFULLY",
                message=BRAND_UPDATED_SUCCESSFULLY,
                data=brand.as_dict,
                status=status.HTTP_200_OK
            )

        # if the brand is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            status=status.HTTP_200_OK
        )

    # If brand does not exist
    except Brand.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="BRAND_DOES_NOT_EXIST",
            message=BRAND_DOES_NOT_EXIST,
            status=status.HTTP_404_NOT_FOUND
        )

    # If category is not found
    except Category.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="CATEGORY_NOT_FOUND",
            message=CATEGORY_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If store is not found
    except Store.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="STORE_NOT_FOUND",
            message=STORE_NOT_FOUND,
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
# Views for updating the attribute
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_attribute(request, attribute_id):
    try:

        # Extracting the user from the request
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

        # Extracting the attribute data from the request
        attribute_data = request.data

        # Getting all the expected keys from the attribute data
        name = attribute_data.get('name', None)
        description = attribute_data.get('description', None)
        category = attribute_data.get('category', None)
        if isinstance(category, str):
            category = int(category)

        is_active = attribute_data.get('is_active', None)

        # Getting the attribute from the database
        attribute = Attribute.objects.get(id=attribute_id)

        # variable to check if the attribute is updated or not
        is_updated = False

        # Updating the attribute
        # if name and name != attribute.name
        if name and name != attribute.name:
            attribute.name = name
            is_updated = True

        # if description and description != attribute.description
        if description and description != attribute.description:
            attribute.description = description
            is_updated = True

        # if category and category != attribute.category.id
        if category and category != attribute.category.id:
            attribute.category = Category.objects.get(id=category)
            is_updated = True

        # if is_active and is_active != attribute.is_active
        if is_active:
            is_active = True if is_active == 'true' else False
            if is_active != attribute.is_active:
                attribute.is_active = is_active
                is_updated = True

        # if the attribute is updated
        if is_updated:
            # Saving the attribute
            attribute.save()

            # Returning the response
            return NetworkResponse.get_json_response(
                message_code="ATTRIBUTE_UPDATED_SUCCESSFULLY",
                message=ATTRIBUTE_UPDATED_SUCCESSFULLY,
                data=attribute.as_dict,
                status=status.HTTP_200_OK
            )

        # if the attribute is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            status=status.HTTP_200_OK
        )

    # If attribute does not exist
    except Attribute.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="ATTRIBUTE_DOES_NOT_EXIST",
            message=ATTRIBUTE_DOES_NOT_EXIST,
            status=status.HTTP_404_NOT_FOUND
        )

    # If category is not found
    except Category.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="CATEGORY_NOT_FOUND",
            message=CATEGORY_NOT_FOUND,
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
# Views for updating the variation attribute
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_variation_attribute(request, variation_attribute_id):
    try:

        # Extracting the user from the request
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

        # Extracting the variation attribute data from the request
        variation_attribute_data = request.data

        # Getting all the expected keys from the variation attribute data
        name = variation_attribute_data.get('name', None)
        description = variation_attribute_data.get('description', None)
        category = variation_attribute_data.get('category', None)
        if isinstance(category, str):
            category = int(category)
        is_active = variation_attribute_data.get('is_active', None)

        # Getting the variation attribute from the database
        variation_attribute = VariationAttribute.objects.get(id=variation_attribute_id)

        # variable to check if the variation attribute is updated or not
        is_updated = False

        # Updating the variation attribute
        # if name and name != variation_attribute.name
        if name and name != variation_attribute.name:
            variation_attribute.name = name
            is_updated = True

        # if description and description != variation_attribute.description
        if description and description != variation_attribute.description:
            variation_attribute.description = description
            is_updated = True

        # if category and category != variation_attribute.category.id
        if category and category != variation_attribute.category.id:
            variation_attribute.category = Category.objects.get(id=category)
            is_updated = True

        # if is_active and is_active != variation_attribute.is_active
        if is_active:
            is_active = True if is_active == 'true' else False
            if is_active != variation_attribute.is_active:
                variation_attribute.is_active = is_active
                is_updated = True

        # if the variation attribute is updated
        if is_updated:
            # Saving the variation attribute
            variation_attribute.save()

            # Returning the response
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_UPDATED_SUCCESSFULLY",
                message=VARIATION_ATTRIBUTE_UPDATED_SUCCESSFULLY,
                data=variation_attribute.as_dict,
                status=status.HTTP_200_OK
            )

        # if the variation attribute is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            status=status.HTTP_200_OK
        )

    # If variation attribute does not exist
    except VariationAttribute.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_NOT_FOUND",
            message=VARIATION_ATTRIBUTE_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If category is not found
    except Category.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="CATEGORY_NOT_FOUND",
            message=CATEGORY_NOT_FOUND,
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
# Views for updating the variation attribute value
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_variation_attribute_value(request, variation_attribute_value_id):
    try:

        # Extracting the user from the request
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

        # Extracting the variation attribute value data from the request
        variation_attribute_value_data = request.data

        # Getting all the expected keys from the variation attribute value data
        value = variation_attribute_value_data.get('value', None)
        # variation_attribute = variation_attribute_value_data.get('variation_attribute', None)
        # if isinstance(variation_attribute, str):
        #     variation_attribute = int(variation_attribute)

        # Getting the variation attribute value from the database
        variation_attribute_value = VariationAttributeValue.objects.get(id=variation_attribute_value_id)

        # variable to check if the variation attribute value is updated or not
        is_updated = False

        # Updating the variation attribute value
        # if value and value != variation_attribute_value.value
        if value and value != variation_attribute_value.value:
            variation_attribute_value.value = value
            is_updated = True

        # if variation_attribute and variation_attribute != variation_attribute_value.variation_attribute.id
        # if variation_attribute and variation_attribute != variation_attribute_value.variation_attribute.id:
        #     variation_attribute_value.variation_attribute = VariationAttribute.objects.get(id=variation_attribute)
        #     is_updated = True

        # if the variation attribute value is updated
        if is_updated:
            # Saving the variation attribute value
            variation_attribute_value.save()

            # Returning the response
            return NetworkResponse.get_json_response(
                message_code="VARIATION_ATTRIBUTE_VALUE_UPDATED_SUCCESSFULLY",
                message=VARIATION_ATTRIBUTE_VALUE_UPDATED_SUCCESSFULLY,
                data=variation_attribute_value.as_dict,
                status=status.HTTP_200_OK
            )

        # if the variation attribute value is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            status=status.HTTP_200_OK
        )

    # If variation attribute value does not exist
    except VariationAttributeValue.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="VARIATION_ATTRIBUTE_VALUE_NOT_FOUND",
            message=VARIATION_ATTRIBUTE_VALUE_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If variation attribute does not exist
    # except VariationAttribute.DoesNotExist:
    #     return NetworkResponse.get_json_response(
    #         message_code="VARIATION_ATTRIBUTE_NOT_FOUND",
    #         message=VARIATION_ATTRIBUTE_NOT_FOUND,
    #         status=status.HTTP_404_NOT_FOUND
    #     )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for updating product attribute
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_product_attribute(request, product_attribute_id):
    try:

        # Extracting the user from the request
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

        # Extracting the product attribute data from the request
        product_attribute_data = request.data

        # Getting all the expected keys from the product attribute data
        # product = product_attribute_data.get('product', None)
        # if isinstance(product, str):
        #     product = int(product)
        #
        # attribute = product_attribute_data.get('attribute', None)
        # if isinstance(attribute, str):
        #     attribute = int(attribute)

        value = product_attribute_data.get('value', None)

        # Getting the product attribute from the database
        product_attribute = ProductAttribute.objects.get(id=product_attribute_id)

        # variable to check if the product attribute is updated or not
        is_updated = False

        # Updating the product attribute
        # if product and product != product_attribute.product.id
        # if product and product != product_attribute.product.id:
        #     product_attribute.product = Product.objects.get(id=product)
        #     is_updated = True

        # if attribute and attribute != product_attribute.attribute.id
        # if attribute and attribute != product_attribute.attribute.id:
        #     product_attribute.attribute = Attribute.objects.get(id=attribute)
        #     is_updated = True

        # if value and value != product_attribute.value
        if value and value != product_attribute.value:
            product_attribute.value = value
            is_updated = True

        # if the product attribute is updated
        if is_updated:
            # Saving the product attribute
            product_attribute.save()

            # Returning the response
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_ATTRIBUTE_UPDATED_SUCCESSFULLY",
                message=PRODUCT_ATTRIBUTE_UPDATED_SUCCESSFULLY,
                data=product_attribute.as_dict,
                status=status.HTTP_200_OK
            )

        # if the product attribute is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            status=status.HTTP_200_OK
        )

    # If product attribute does not exist
    except ProductAttribute.DoesNotExist:
        return NetworkResponse.get_json_response(
            message_code="PRODUCT_ATTRIBUTE_NOT_FOUND",
            message=PRODUCT_ATTRIBUTE_NOT_FOUND,
            status=status.HTTP_404_NOT_FOUND
        )

    # If product does not exist
    # except Product.DoesNotExist:
    #     return NetworkResponse.get_json_response(
    #         message_code="PRODUCT_NOT_FOUND",
    #         message=PRODUCT_NOT_FOUND,
    #         status=status.HTTP_404_NOT_FOUND
    #     )

    # If attribute does not exist
    # except Attribute.DoesNotExist:
    #     return NetworkResponse.get_json_response(
    #         message_code="ATTRIBUTE_DOES_NOT_EXIST",
    #         message=ATTRIBUTE_DOES_NOT_EXIST,
    #         status=status.HTTP_404_NOT_FOUND
    #     )

    # If any exception occurs
    except Exception as e:
        return NetworkResponse.get_json_response(
            message_code='EXCEPTION',
            message=str(e),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------------------@mit-----------------------------------
# Views for updating product price
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_product_price(request, product_price_id):
    try:

        # Extracting the user from the request
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

        # Extracting the product price data from the request
        product_price_data = request.data

        # Getting all the expected keys from the product price data
        sp = product_price_data.get('sp', None)
        mrp = product_price_data.get('mrp', None)

        # Getting the product price from the database
        product_price = ProductPrice.objects.get(id=product_price_id)

        # variable to check if the product price is updated or not
        is_updated = False

        # Updating the product price
        # if sp and sp != product_price.sp
        if sp and sp != product_price.sp:
            product_price.sp = sp
            is_updated = True

        # if mrp and mrp != product_price.mrp
        if mrp and mrp != product_price.mrp:
            product_price.mrp = mrp
            is_updated = True

        # if the product price is updated
        if is_updated:
            # Saving the product price
            product_price.save()

            # Returning the response
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_PRICE_UPDATED_SUCCESSFULLY",
                message=PRODUCT_PRICE_UPDATED_SUCCESSFULLY,
                data=product_price.as_dict,
                status=status.HTTP_200_OK
            )

        # if the product price is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            status=status.HTTP_200_OK
        )

    # If product price does not exist
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
# Views for updating product stock
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_product_stock(request, product_stock_id):
    try:

        # Extracting the user from the request
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

        # Extracting the product stock data from the request
        product_stock_data = request.data

        # Getting all the expected keys from the product stock data
        quantity = product_stock_data.get('quantity', None)

        # Getting the product stock from the database
        product_stock = ProductStock.objects.get(id=product_stock_id)

        # variable to check if the product stock is updated or not
        is_updated = False

        # Updating the product stock
        # if quantity and quantity != product_stock.quantity
        if quantity and quantity != product_stock.quantity:
            product_stock.quantity = quantity
            is_updated = True

        # if the product stock is updated
        if is_updated:
            # Saving the product stock
            product_stock.save()

            # Returning the response
            return NetworkResponse.get_json_response(
                message_code="PRODUCT_STOCK_UPDATED_SUCCESSFULLY",
                message=PRODUCT_STOCK_UPDATED_SUCCESSFULLY,
                data=product_stock.as_dict,
                status=status.HTTP_200_OK
            )

        # if the product stock is not updated
        return NetworkResponse.get_json_response(
            message_code="NO_CHANGES_MADE",
            message=NO_CHANGES_MADE,
            status=status.HTTP_200_OK
        )

    # If product stock does not exist
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

# -----------------------------------@mit-----------------------------------
# Views for updating product
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# def update_product(request, product_id):
#     try:
#
#         # Extracting the user from the request
#         user = request.user
#
#         # Check if user is active
#         if not user.is_active:
#             return NetworkResponse.get_json_response(
#                 message_code="ACCOUNT_NOT_ACTIVATED",
#                 message=ACCOUNT_NOT_ACTIVATED,
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Check if user is super_admin or store_admin or store_staff
#         if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
#             return NetworkResponse.get_json_response(
#                 message_code="ACCESS_DENIED",
#                 message=ACCESS_DENIED,
#                 status=status.HTTP_403_FORBIDDEN
#             )
#
#         # Extracting the product data from the request
#         product_data = request.data
#
#         # Getting all the expected keys from the product data
#         name = product_data.get('name', None)
#         description = product_data.get('description', None)
#         sp = product_data.get('sp', None)
#         mrp = product_data.get('mrp', None)
#         quantity = product_data.get('quantity', None)
#         category = product_data.get('category', None)
#
