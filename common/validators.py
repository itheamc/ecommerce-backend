import re


class Validators:

    # Method to validate if a string is a valid email
    @staticmethod
    def validate_email(email):
        if len(email) > 7:
            if re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email) is not None:
                return True
        return False

    # Method to validate password
    @staticmethod
    def validate_password(password):
        if len(password) > 7:
            return True
        return False

    # Method to validate if the phone number is valid
    @staticmethod
    def validate_phone(phone):
        if len(phone) == 10:
            if re.match("^[0-9]+$", phone) is not None:
                return True
        return False

    # Method to validate pan number
    @staticmethod
    def validate_pan(pan):
        if len(pan) >= 9:
            if re.match("^[0-9]+$", pan) is not None:
                return True
        return False

    # Method to validate address
    @staticmethod
    def validate_address(address):
        if address is not None and 'city' in address and 'ward_number' in address and 'municipality' in address and 'district' in address and 'province' in address and 'country' in address and 'postal_code' in address:
            return True
        return False

    # Method to validate if the user data is a valid
    @staticmethod
    def validate_user_data(user_data):
        if user_data is not None and 'first_name' in user_data and 'email' in user_data and 'phone' in user_data:
            return True
        return False

    # Method to validate if the store staff data is a valid
    @staticmethod
    def validate_store_staff_data(store_staff_data):
        if store_staff_data is not None and Validators.validate_user_data(
                store_staff_data['user']) and 'position' in store_staff_data:
            return True
        return False
