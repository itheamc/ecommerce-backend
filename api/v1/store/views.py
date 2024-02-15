import random
import string

from django.contrib.auth import authenticate
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from authentication.models import ASquareUser, TempASquareUser
from common.handlers import MailHandler
from common.literals import *
from common.models import Category
from common.response import NetworkResponse
from common.validators import Validators
from store.models import Store, StoreAddress, StoreStaff


# -----------------------------------@mit-------------------------------
# Method to register a seller
@csrf_exempt
@api_view(['POST'])
def register_a_seller(request):
    try:
        # Extracting seller data from the request
        seller_data = request.data

        # Checking if the seller data contains all the required fields
        if 'first_name' not in seller_data:
            return JsonResponse(NetworkResponse(message_code='STORE_NAME_REQUIRED', message=STORE_NAME_REQUIRED).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        if 'email' not in seller_data:
            return JsonResponse(NetworkResponse(message_code='EMAIl_REQUIRED', message=EMAIL_REQUIRED).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        if 'phone' in seller_data and not Validators.validate_phone(seller_data['phone']):
            return JsonResponse(NetworkResponse(message_code='INVALID_PHONE_NUMBER', message=INVALID_PHONE_NUMBER).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        if not Validators.validate_email(seller_data['email']):
            return JsonResponse(NetworkResponse(message_code='INVALID_EMAIL', message=INVALID_EMAIL).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        if 'password' not in seller_data:
            return JsonResponse(NetworkResponse(message_code='PASSWORD_REQUIRED', message=PASSWORD_REQUIRED).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # If all the required fields are present
        # Creating the user as an owner for the store
        email = seller_data.pop('email')
        password = seller_data.pop('password')

        # Checking if the email already exists
        user = ASquareUser.objects.filter(email=email)
        if user.exists():
            return JsonResponse(NetworkResponse(message_code='EMAIL_ALREADY_EXISTS', message=EMAIL_ALREADY_EXISTS).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # Checking if the phone number already exists
        if 'phone' in seller_data:
            user = ASquareUser.objects.filter(phone=seller_data['phone'])
            if user.exists():
                return JsonResponse(NetworkResponse(message_code='PHONE_NUMBER_ALREADY_EXISTS',
                                                    message=PHONE_NUMBER_ALREADY_EXISTS).to_json(),
                                    status=status.HTTP_400_BAD_REQUEST)

        # Popping the is_super_admin field from the seller data if present
        if 'is_super_admin' in seller_data:
            seller_data.pop('is_super_admin')

        # Popping the is_active field from the seller data if present
        if 'is_active' in seller_data:
            seller_data.pop('is_active')

        # If the email and phone number are not present or are not already registered
        user = ASquareUser.objects.create_user(email=email, password=password, **seller_data)
        user.is_staff = True
        user.is_store_admin = True
        user.save()

        # Generating 5 digit random otp and encrypting it using the timestamp signer and
        # Sending the otp to the user's email
        MailHandler.generate_n_send_otp(to=user)

        # Returning the store
        return JsonResponse(
            NetworkResponse(message_code='OTP_SENT_SUCCESSFULLY', message=OTP_SENT_SUCCESSFULLY).to_json(),
            status=status.HTTP_200_OK)
    # If any error occurs
    except Exception as e:
        return JsonResponse(NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to verify the seller's otp
@csrf_exempt
@api_view(['POST'])
def seller_otp_verify(request):
    try:
        # Extracting otp data
        otp_data = request.data

        # Checking if the otp data contains all the required fields
        if 'email' not in otp_data:
            return JsonResponse(NetworkResponse(message_code='EMAIL_REQUIRED', message=EMAIL_REQUIRED).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        if not Validators.validate_email(otp_data['email']):
            return JsonResponse(NetworkResponse(message_code='INVALID_EMAIL', message=INVALID_EMAIL).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        if 'otp' not in otp_data:
            return JsonResponse(NetworkResponse(message_code='OTP_CODE_REQUIRED', message=OTP_CODE_REQUIRED).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # If otp is not a number
        if otp_data['otp'].isdigit() is False:
            return JsonResponse(
                NetworkResponse(message_code='OTP_MUST_BE_IN_NUMBER', message=OTP_MUST_BE_IN_NUMBER).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        # If all the required fields are present
        email = otp_data.pop('email')
        otp = otp_data.pop('otp')

        # Getting temp user from the database
        temp_user = TempASquareUser.objects.filter(email=email)

        # Checking if the temp user doesn't exist
        if not temp_user.exists():
            return JsonResponse(
                NetworkResponse(message_code='SIGNUP_FIRST_TO_VERIFY_OTP', message=SIGNUP_FIRST_TO_VERIFY_OTP).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        encrypted_otp = temp_user.first().otp
        signer = TimestampSigner(salt=OTP_SALT)
        decrypted_otp = signer.unsign(encrypted_otp, max_age=600)

        # Checking if the otp is valid
        if otp != decrypted_otp:
            return JsonResponse(NetworkResponse(message_code='INVALID_OTP_CODE', message=INVALID_OTP_CODE).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # Getting the user from the database
        users = ASquareUser.objects.filter(email=email)

        # Checking if the user doesn't exist
        if not users.exists():
            return JsonResponse(NetworkResponse(message_code='USER_NOT_FOUND', message=USER_NOT_FOUND).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # If the user exists
        user = users.first()

        # Deleting the temp user from the database
        temp_user.delete()

        # Updating the user's is_active field to True
        user.is_active = True
        user.save()

        # Getting the token
        token = Token.objects.get_or_create(user=user)[0].key

        # Returning the user's token
        return JsonResponse(
            NetworkResponse(message_code='OTP_VERIFICATION_SUCCESS', message=OTP_VERIFICATION_SUCCESS, token=token).to_json(),
            status=status.HTTP_200_OK)

    # If otp exceeds the max age
    except SignatureExpired:
        return JsonResponse(NetworkResponse(message_code='OTP_CODE_EXPIRED', message=OTP_CODE_EXPIRED).to_json(),
                            status=status.HTTP_400_BAD_REQUEST)

    # If Bad Signature
    except BadSignature:
        return JsonResponse(NetworkResponse(message_code='INVALID_OTP_CODE', message=INVALID_OTP_CODE).to_json(),
                            status=status.HTTP_400_BAD_REQUEST)

    # If any error occurs
    except Exception as e:
        return JsonResponse(NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to handle seller or staff login
@csrf_exempt
@api_view(['POST'])
def seller_or_staff_login(request):
    try:
        # Extracting the data from the request
        login_data = request.data

        # If email not in login data
        if 'email' not in login_data:
            return JsonResponse(
                NetworkResponse(message_code='EMAIl_REQUIRED', message=EMAIL_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        # If email is invalid
        if not Validators.validate_email(login_data['email']):
            return JsonResponse(NetworkResponse(message_code='INVALID_EMAIL', message=INVALID_EMAIL).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # If password not in login data
        if 'password' not in login_data:
            return JsonResponse(
                NetworkResponse(message_code='PASSWORD_REQUIRED', message=PASSWORD_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        # If all the required fields are present, then extracting address and owner data from it
        email = login_data.get('email')
        password = login_data.get('password')

        # Validating the email and password
        user = authenticate(request, email=email, password=password)

        # If the user is not found
        if user is None:
            return JsonResponse(
                NetworkResponse(message_code='PROVIDE_VALID_CREDENTIALS', message=PROVIDE_VALID_CREDENTIALS).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        # If the user is not a staff
        if not user.is_staff:
            return JsonResponse(NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                                status=status.HTTP_401_UNAUTHORIZED)

        # If the user is found but is inactive
        if not user.is_active:
            # Generating 5 digit random otp and encrypting it using the timestamp signer and
            # Sending the otp to the user's email
            MailHandler.generate_n_send_otp(to=user)

            return JsonResponse(
                NetworkResponse(message_code='ACCOUNT_NOT_ACTIVATED', message=ACCOUNT_NOT_ACTIVATED).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        # Getting store from the staff object
        store = user.staff.store if user.is_staff else None

        # Getting the token
        token = Token.objects.get_or_create(user=user)[0].key
        # Returning the store
        return JsonResponse(NetworkResponse(message_code='LOGIN_SUCCESSFUL', message=LOGIN_SUCCESSFUL, token=token).to_json(),
                            status=status.HTTP_200_OK, safe=False)

    # If store staff not found
    except StoreStaff.DoesNotExist:
        return JsonResponse(NetworkResponse(message_code='NOT_STAFF_OF_STORE', message=NOT_STAFF_OF_STORE).to_json(),
                            status=status.HTTP_404_NOT_FOUND)

    # If store staff not found
    except Store.DoesNotExist:
        return JsonResponse(NetworkResponse(message_code='STAFF_STORE_NOT_FOUND', message=STAFF_STORE_NOT_FOUND).to_json(),
                            status=status.HTTP_404_NOT_FOUND)

    # If any error occurs
    except Exception as e:
        return JsonResponse(NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to add a store
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_a_store(request):
    try:
        # Extracting the user
        user = request.user

        # If user is not active
        if not user.is_active:
            return JsonResponse(
                NetworkResponse(message_code='ACCOUNT_NOT_ACTIVATED', message=ACCOUNT_NOT_ACTIVATED).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_store_admin:
            return JsonResponse(NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                                status=status.HTTP_401_UNAUTHORIZED)

        # Extracting store data from the request
        store_data = request.data

        # Checking if the store data contains all the required fields
        if 'category' not in store_data:
            return JsonResponse(
                NetworkResponse(message_code='STORE_CATEGORY_REQUIRED', message=STORE_CATEGORY_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        if 'name' not in store_data:
            return JsonResponse(
                NetworkResponse(message_code='STORE_NAME_REQUIRED', message=STORE_NAME_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        if 'phone' not in store_data:
            return JsonResponse(
                NetworkResponse(message_code='STORE_PHONE_REQUIRED', message=STORE_PHONE_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        if not Validators.validate_phone(store_data['phone']):
            return JsonResponse(
                NetworkResponse(message_code='INVALID_PHONE_NUMBER', message=INVALID_PHONE_NUMBER).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        if 'email' in store_data and not Validators.validate_email(store_data['email']):
            return JsonResponse(
                NetworkResponse(message_code='INVALID_EMAIL', message=INVALID_EMAIL).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        if 'pan_number' not in store_data:
            return JsonResponse(
                NetworkResponse(message_code='STORE_PAN_NUMBER_REQUIRED', message=STORE_PAN_NUMBER_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        if 'address' not in store_data:
            return JsonResponse(
                NetworkResponse(message_code='STORE_ADDRESS_REQUIRED', message=STORE_ADDRESS_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        if not Validators.validate_address(store_data['address']):
            return JsonResponse(
                NetworkResponse(message_code='STORE_ADDRESS_INVALID', message=STORE_ADDRESS_INVALID).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        # If all the required fields are present, then extracting address and owner data from it
        address_data = store_data.pop('address')
        category_id = store_data.pop('category')

        # Creating a new store
        store = Store.objects.create(owner=user, category_id=category_id, **store_data)

        # Creating the address for the store
        StoreAddress.objects.create(store=store, **address_data)

        # Returning the store
        return JsonResponse(NetworkResponse(message_code='STORE_ADDED_SUCCESSFULLY', message=STORE_ADDED_SUCCESSFULLY,
                                            data=store.as_dict).to_json(), status=status.HTTP_200_OK)
    # If any error occurs
    except Exception as e:
        return JsonResponse(
            NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to add a store
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_a_store(request, store_id=None):
    try:
        # If store id is not provided
        if not store_id:
            return JsonResponse(NetworkResponse(message_code='STORE_ID_REQUIRED', message=STORE_ID_REQUIRED).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # Extracting the user
        user = request.user

        # If user is not active
        if not user.is_active:
            return JsonResponse(
                NetworkResponse(message_code='ACCOUNT_NOT_ACTIVATED', message=ACCOUNT_NOT_ACTIVATED).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_store_admin:
            return JsonResponse(NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                                status=status.HTTP_401_UNAUTHORIZED)

        # Extracting store data from the request to update
        update_data = request.data

        # If update data contains any of the store fields
        if 'category' in update_data or 'name' in update_data or 'tag_line' in update_data or 'phone' in update_data or 'email' in update_data or 'pan_number' in update_data or 'is_active' in update_data:

            if 'phone' in update_data and not Validators.validate_phone(update_data['phone']):
                return JsonResponse(
                    NetworkResponse(message_code='INVALID_PHONE_NUMBER', message=INVALID_PHONE_NUMBER).to_json(),
                    status=status.HTTP_400_BAD_REQUEST)

            if 'email' in update_data and not Validators.validate_email(update_data['email']):
                return JsonResponse(
                    NetworkResponse(message_code='INVALID_EMAIL', message=INVALID_EMAIL).to_json(),
                    status=status.HTTP_400_BAD_REQUEST)

            if 'pan_number' in update_data and not Validators.validate_pan(update_data['pan_number']):
                return JsonResponse(
                    NetworkResponse(message_code='INVALID_PAN_NUMBER', message=INVALID_PAN_NUMBER).to_json(),
                    status=status.HTTP_400_BAD_REQUEST)

            # Extracting all the store data from the request
            category_id = update_data.get('category')
            name = update_data.get('name')
            tag_line = update_data.get('tag_line')
            phone = update_data.get('phone')
            email = update_data.get('email')
            pan_number = update_data.get('pan_number')
            is_active = update_data.get('is_active')

            # Getting user's store
            store = Store.objects.get(id=store_id)

            if not user.id == store.owner.id:
                return JsonResponse(
                    NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                    status=status.HTTP_401_UNAUTHORIZED)

            # Updating the store
            is_updated = False
            if category_id and category_id != store.category.id:
                category = Category.objects.get(id=category_id)
                store.category = category
                is_updated = True
            if name and name.strip().__len__() > 0 and name.strip() != store.name:
                store.name = name
                is_updated = True
            if tag_line and tag_line.strip().__len__() > 0 and tag_line.strip() != store.tag_line:
                store.tag_line = tag_line
                is_updated = True
            if phone and phone.strip() != store.phone:
                store.phone = phone
                is_updated = True
            if email and email.strip() != store.email:
                store.email = email
                is_updated = True
            if pan_number and pan_number.strip() != store.pan_number:
                store.pan_number = pan_number
                is_updated = True
            if is_active is not None and is_active != store.is_active:
                store.is_active = is_active
                is_updated = True

            # If store is updated
            if is_updated:
                store.save()

            # Return to success response
            return JsonResponse(NetworkResponse(message_code='STORE_UPDATED_SUCCESSFULLY', message=STORE_UPDATED_SUCCESSFULLY,
                                                data=store.as_dict).to_json(), status=status.HTTP_200_OK)

    # If store not found
    except Store.DoesNotExist:
        return JsonResponse(NetworkResponse(message_code='STORE_NOT_FOUND', message=STORE_NOT_FOUND).to_json(),
                            status=status.HTTP_400_BAD_REQUEST)
    # If store not found
    except Category.DoesNotExist:
        return JsonResponse(
            NetworkResponse(message_code='STORE_CATEGORY_NOT_FOUND', message=STORE_CATEGORY_NOT_FOUND).to_json(),
            status=status.HTTP_400_BAD_REQUEST)
    # If any error occurs
    except Exception as e:
        return JsonResponse(
            NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to get stores
# For super admin only
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_stores(request):
    try:
        # extracting user from the request
        user = request.user

        # if the user is not active
        if not user.is_active:
            return JsonResponse(
                NetworkResponse(message_code='ACCOUNT_NOT_ACTIVATED', message=ACCOUNT_NOT_ACTIVATED).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        # If user is not super admin and not store admin
        if not user.is_super_admin and not user.is_store_admin:
            return JsonResponse(NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                                status=status.HTTP_401_UNAUTHORIZED)

        # If user is super admin
        if user.is_super_admin:
            # getting the stores
            stores = Store.objects.all()
            # converting the stores to a list of dicts
            stores_res = [store.as_dict for store in stores]
            # returning the stores
            return JsonResponse(NetworkResponse(message_code='STORE_LIST_RETRIEVED', message=STORE_LIST_RETRIEVED,
                                                data=stores_res).to_json(), status=status.HTTP_200_OK)
        # If user is store admin
        else:
            # getting the stores
            stores = Store.objects.filter(owner=user)
            # converting the stores to a list of dicts
            stores_res = [store.as_dict for store in stores]
            # returning the stores
            return JsonResponse(NetworkResponse(message_code='STORE_LIST_RETRIEVED', message=STORE_LIST_RETRIEVED,
                                                data=stores_res).to_json(), status=status.HTTP_200_OK)

    # If any error occurs
    except Exception as e:
        return JsonResponse(
            NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to get a store
# By store id or as per the requested user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_a_store(request, store_id=None):
    try:

        # If store id is not provided
        if not store_id:
            return JsonResponse(NetworkResponse(message_code='STORE_ID_REQUIRED', message=STORE_ID_REQUIRED).to_json(),
                                status=status.HTTP_400_BAD_REQUEST)

        # extracting user from the request
        user = request.user

        # If user is not active
        if not user.is_active:
            return JsonResponse(
                NetworkResponse(message_code='ACCOUNT_NOT_ACTIVATED', message=ACCOUNT_NOT_ACTIVATED).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        # if the store_id is Not None, getting the store
        store = Store.objects.get(id=store_id)
        # converting the store obj to a dict
        store_res = store.as_dict if user.is_super_admin else store.as_dict_min
        # returning the store
        return JsonResponse(
            NetworkResponse(message_code='STORE_RETRIEVED', message=STORE_RETRIEVED, data=store_res).to_json(),
            status=status.HTTP_200_OK)

    # If store not found
    except Store.DoesNotExist:
        return JsonResponse(NetworkResponse(message_code='STORE_NOT_FOUND', message=STORE_NOT_FOUND).to_json(),
                            status=status.HTTP_400_BAD_REQUEST)

    # If any error occurs
    except Exception as e:
        return JsonResponse(NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to add a store staff
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_store_staff(request):
    try:
        # extracting user from the request
        user = request.user

        # If user is inactive
        if not user.is_active:
            return JsonResponse(
                NetworkResponse(message_code='ACCOUNT_NOT_ACTIVATED', message=ACCOUNT_NOT_ACTIVATED).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        # If user is not store admin
        if not user.is_store_admin:
            return JsonResponse(NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                                status=status.HTTP_401_UNAUTHORIZED)

        # getting the data from the request
        staff_data = request.data

        # if staff_data does not exist or does not contain the required fields
        if not staff_data or not Validators.validate_store_staff_data(staff_data):
            return JsonResponse(
                NetworkResponse(message_code='PROVIDE_ALL_REQUIRED_FIELDS', message=PROVIDE_ALL_REQUIRED_FIELDS).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

        # if everything is fine
        # Extracting the user data from the staff_data
        user_data = staff_data.pop('user')

        # Extract email from user data
        email = user_data.pop('email')

        # Generating temporary password
        temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

        # Creating user
        staff_user = ASquareUser.objects.create_user(email=email, password=temp_password, **user_data)

        # Getting store from the requested user
        store = user.store

        # Creating new staff
        staff = StoreStaff.objects.create(user=staff_user, store=store, **staff_data)

        # Send password in the email

    # If store not found
    except Store.DoesNotExist:
        return JsonResponse(NetworkResponse(message_code='STORE_NOT_FOUND', message=STORE_NOT_FOUND).to_json(),
                            status=status.HTTP_400_BAD_REQUEST)

    # if any error occurs
    except Exception as e:
        return JsonResponse(
            NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-------------------------------
# Method to get a store staff
# By store staff id or as per the requested user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_store_staff(request, staff_id=None):
    try:
        # extracting user from the request
        user = request.user

        # If user is inactive
        if not user.is_active:
            return JsonResponse(
                NetworkResponse(message_code='ACCOUNT_NOT_ACTIVATED', message=ACCOUNT_NOT_ACTIVATED).to_json(),
                status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_super_admin and not user.is_store_admin and not user.is_staff:
            return JsonResponse(NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                                status=status.HTTP_401_UNAUTHORIZED)

        # if the store_staff_id is Not None
        if staff_id is not None:
            # If user is super admin
            if user.is_super_admin:
                # getting the store staff
                store_staff = StoreStaff.objects.get(id=staff_id)

                # converting the store staff obj to a dict
                store_staff_res = store_staff.as_dict

                # returning the store staff
                return JsonResponse(NetworkResponse(message_code='STORE_STAFF_RETRIEVED', message=STORE_STAFF_RETRIEVED,
                                                    data=store_staff_res).to_json(), status=status.HTTP_200_OK)

            # If user is store admin or staff
            if user.is_store_admin or user.is_staff:
                # getting the store staff
                store_staff = StoreStaff.objects.get(id=staff_id)

                if (user.is_store_admin and not store_staff.store.id == user.store.id) or (
                        user.is_staff and not store_staff.store.id == user.staff.store.id):
                    return JsonResponse(
                        NetworkResponse(message_code='UNAUTHORIZED', message=UNAUTHORIZED).to_json(),
                        status=status.HTTP_401_UNAUTHORIZED)

                # converting the store staff obj to a dict
                store_staff_res = store_staff.as_dict if user.is_store_admin else store_staff.as_dict_min
                # returning the store staff
                return JsonResponse(NetworkResponse(message_code='STORE_STAFF_RETRIEVED', message=STORE_STAFF_RETRIEVED,
                                                    data=store_staff_res).to_json(), status=status.HTTP_200_OK)

            # if the store_staff_id is None
            if user.is_staff and not user.is_store_admin:
                # Getting the store staff from the user
                store_staff = user.staff

                # converting the store staff obj to a dict
                store_staff_res = store_staff.as_dict_min
                # returning the store staff
                return JsonResponse(
                    NetworkResponse(message_code='STORE_STAFF_RETRIEVED', message=STORE_STAFF_RETRIEVED,
                                    data=store_staff_res).to_json(), status=status.HTTP_200_OK)

            # if the user is not a store admin or staff
            return JsonResponse(
                NetworkResponse(message_code='STAFF_ID_REQUIRED', message=STAFF_ID_REQUIRED).to_json(),
                status=status.HTTP_400_BAD_REQUEST)

    # If store staff does not exist
    except Store.DoesNotExist:
        return JsonResponse(NetworkResponse(message_code='STORE_NOT_FOUND', message=STORE_NOT_FOUND).to_json(),
                            status=status.HTTP_400_BAD_REQUEST)

    # If store staff does not exist
    except StoreStaff.DoesNotExist:
        return JsonResponse(NetworkResponse(message_code='STORE_STAFF_NOT_FOUND', message=STORE_STAFF_NOT_FOUND).to_json(),
                            status=status.HTTP_400_BAD_REQUEST)

    # If any error occurs
    except Exception as e:
        return JsonResponse(NetworkResponse(message_code='EXCEPTION', message=str(e)).to_json(),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
