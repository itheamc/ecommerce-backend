from django.db import models


# ----------------------------@amit--------------------------------
# Customer Model
class Customer(models.Model):
    user = models.OneToOneField('authentication.ASquareUser', on_delete=models.CASCADE, related_name='customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # property for customer addresses
    @property
    def addresses(self):
        return self.address_set.all()

    # Property to get the dict of customer
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'phone': self.user.phone,
            'addresses': [address.as_dict for address in self.addresses.all()],
        }

    # Property to get the dict min of customer
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'phone': self.user.phone,
        }

    def __str__(self):
        return self.user.full_name

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'


# ----------------------------@amit--------------------------------
# Customer Address Model
class CustomerAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='address_set')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    ward_number = models.CharField(max_length=5)
    municipality = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    receiver_name = models.CharField(max_length=255)
    receiver_phone = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # property for full address
    @property
    def full_address(self):
        return '{}-{}, {}, {}'.format(self.municipality, self.ward_number, self.district, self.province)

    # property for customer address dict
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'street': self.street,
            'city': self.city,
            'ward_number': self.ward_number,
            'municipality': self.municipality,
            'district': self.district,
            'province': self.province,
            'country': self.country,
            'postal_code': self.postal_code,
            'receiver_name': self.receiver_name,
            'receiver_phone': self.receiver_phone
        }

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'Customer Address'
        verbose_name_plural = 'Customer Addresses'
