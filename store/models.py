from django.db import models


# ----------------------------@amit--------------------------------
# Store Model
class Store(models.Model):
    STORE_TYPE_SELECTION = (('retail', 'Retail'), ('wholesale', 'Wholesale'), ('dealer', 'Dealer'), ('other', 'Other'))

    name = models.CharField(max_length=255)
    tag_line = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    logo = models.FileField(upload_to='assets/store/logo/', blank=True, null=True)
    pan_number = models.CharField(max_length=50)
    category = models.ForeignKey('common.Category', on_delete=models.PROTECT, blank=True, null=True,
                                 related_name='store_category')
    type = models.CharField(max_length=20, choices=STORE_TYPE_SELECTION, default='retail')
    owner = models.ForeignKey('authentication.ASquareUser', on_delete=models.PROTECT, related_name='stores')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # property for logo url
    @property
    def logo_url(self):
        return self.logo.url if self.logo else None

    # property for store address
    @property
    def address(self):
        return self.addresses.first() if self.addresses.exists() and self.addresses.count() > 0 else None

    # property for store dict
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tag_line': self.tag_line,
            'phone': self.phone,
            'email': self.email,
            'logo': self.logo_url,
            'pan_number': self.pan_number,
            'category': self.category.as_nested_dict if self.category else None,
            'store_type': self.type,
            'owner': self.owner.as_dict_min if self.owner else None,
            'address': self.address.as_dict if self.address else None,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # property for store dict
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'name': self.name,
            'tag_line': self.tag_line,
            'phone': self.phone,
            'email': self.email,
            'logo': self.logo_url,
            'pan_number': self.pan_number,
            'category': self.category.as_nested_dict if self.category else None,
            'store_type': self.type,
            'address': self.address.as_dict if self.address else None,
            'is_active': self.is_active,
            'is_approved': self.is_approved
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'


# ----------------------------@amit--------------------------------
# StoreStaff Model
class StoreStaff(models.Model):
    user = models.OneToOneField('authentication.ASquareUser', on_delete=models.CASCADE, related_name='staff')
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='staffs')
    position = models.ForeignKey('store.StoreStaffPosition', on_delete=models.PROTECT, related_name='staffs',
                                 null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # property for store staff dict
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'user': self.user.as_dict_min if self.user else None,
            'store': self.store.as_dict_min if self.store else None,
            'position': self.position.as_dict if self.position else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # property for store staff dict
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'user': self.user.as_dict_min if self.user else None,
            'position': self.position.as_dict if self.position else None
        }

    def __str__(self):
        return self.user.full_name

    class Meta:
        verbose_name = 'Store Staff'
        verbose_name_plural = 'Store Staffs'


# ----------------------------@amit--------------------------------
# StoreStaffPosition Model
class StoreStaffPosition(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # property for store staff position dict
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Store Staff Position'
        verbose_name_plural = 'Store Staff Positions'


# ----------------------------@amit--------------------------------
# StoreAddress Model
class StoreAddress(models.Model):
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    ward_number = models.CharField(max_length=5)
    municipality = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # property for full address
    @property
    def full_address(self):
        return '{}-{}, {}, {}'.format(self.municipality, self.ward_number, self.district, self.province)

    # property for store address dict
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
            'postal_code': self.postal_code
        }

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'Store Address'
        verbose_name_plural = 'Store Addresses'
