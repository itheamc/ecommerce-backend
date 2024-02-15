from django.db import models

# ----------------------------------@mit----------------------------------
# Attribute Model
from django.db.models import Avg


class Attribute(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True, null=True)
    category = models.ForeignKey('common.Category', on_delete=models.CASCADE, related_name='attributes')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'

    def __str__(self):
        return self.name

    # Property to get total products with a attribute
    @property
    def total_products(self):
        return self.product_attributes.count()

    # Property to get the dict of attribute
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the min dict of attribute
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    # Property to get the dict of attribute details
    @property
    def as_dict_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'category': self.category.as_dict_min,
            'total_products': self.total_products,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


# ----------------------------------@mit----------------------------------
# Variation Attribute Model
class VariationAttribute(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=220, blank=True, null=True)
    category = models.ForeignKey('common.Category', on_delete=models.CASCADE, related_name='variation_attributes')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Variation Attribute'
        verbose_name_plural = 'Variation Attributes'

    def __str__(self):
        return self.name

    # Property to get dict of variation
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }

    # Property to get min dict of variation
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    # Property to get dict of variation with values
    @property
    def as_dict_with_values(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'values': [value.as_dict for value in self.variation_attribute_values.all()]
        }

    # Property to get dict of variation attribute details
    @property
    def as_dict_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'category': self.category.as_dict_min,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


# ----------------------------------@mit----------------------------------
# Variation Attribute Value Model
class VariationAttributeValue(models.Model):
    variation_attribute = models.ForeignKey('VariationAttribute', on_delete=models.CASCADE,
                                            related_name='variation_attribute_values')
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Variation Attribute Value'
        verbose_name_plural = 'Variation Attribute Values'

    def __str__(self):
        return self.value

    # Property to get total products with a variation attribute value
    @property
    def total_products(self):
        return self.product_variations.count()

    # Property to get dict of variation value
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'variation_attribute': self.variation_attribute.as_dict_min,
            'value': self.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get min dict of variation value
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'value': self.value,
        }

    # Property to get dict of variation value details
    @property
    def as_dict_details(self):
        return {
            'id': self.id,
            'variation_attribute': self.variation_attribute.as_dict_min,
            'value': self.value,
            'total_products': self.total_products,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


# ----------------------------------@mit----------------------------------
# Product Model
class Product(models.Model):
    PRODUCT_STATUS_CHOICES = (('published', 'Published'), ('draft', 'Draft'), ('deleted', 'Deleted'))

    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='products')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, blank=True, null=True)
    category = models.ForeignKey('common.Category', on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT, related_name='products')
    variation_attribute_value = models.ForeignKey('VariationAttributeValue', on_delete=models.PROTECT, blank=True,
                                                  null=True, related_name='product_variations')
    sku = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=15, choices=PRODUCT_STATUS_CHOICES, default='draft')
    tags = models.CharField(max_length=1000, blank=True, null=True, default='')
    slung = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    # Property to check if product is base product
    @property
    def is_base_product(self):
        return self.parent is None

    # Property to get the base product
    @property
    def base_product(self):
        if self.is_base_product:
            return self
        elif self.parent.is_base_product:
            return self.parent
        elif self.parent.parent.is_base_product:
            return self.parent.parent
        elif self.parent.parent.parent.is_base_product:
            return self.parent.parent.parent
        elif self.parent.parent.parent.parent.is_base_product:
            return self.parent.parent.parent.parent
        else:
            return self.parent.parent.parent.parent.parent

    # Property to get the variation_attribute
    @property
    def variation_attribute(self):
        return self.variation_attribute_value.variation_attribute if self.variation_attribute_value else None

    # Property to get the product attributes
    @property
    def attributes(self):
        return self.product_attributes.all()

    # property to get the latest price of product
    @property
    def latest_price(self):
        return self.product_prices.order_by('-created_at').first() if self.product_prices.exists() else None

    # Property to get the total stocks
    @property
    def total_stocks(self):
        return sum([stock.quantity for stock in self.product_stocks.all()])

    # Property to get the thumbnail url
    @property
    def thumbnail_url(self):
        return self.product_images.first().image_url if self.product_images.exists() and self.product_images.first() else None

    # Property to get all the images of product
    @property
    def images(self):
        return self.product_images.all()

    # Property to get latest 5 reviews of product if it is base product else get the reviews of base product
    @property
    def latest_reviews(self):
        if self.is_base_product:
            return self.product_reviews.order_by('-created_at').all()[:5]
        else:
            return self.base_product.product_reviews.order_by('-created_at').all()[:5]

    # Property to get average rating of product if it is base product else get average rating of base product
    @property
    def average_rating(self):
        return self.product_reviews.aggregate(Avg('rating'))['rating__avg'] if self.is_base_product else \
            self.base_product.product_reviews.aggregate(Avg('rating'))[
                'rating__avg'] if self.base_product.product_reviews.exists() else 0

    # Property to get the dict of product
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'store': self.store.id,
            'parent': self.parent.id if self.parent else None,
            'name': self.name,
            'description': self.description,
            'category': self.category.as_dict,
            'brand': self.brand.as_dict,
            'variation_attribute': self.variation_attribute.as_dict if self.variation_attribute else None,
            'variation_attribute_value': self.variation_attribute_value.as_dict if self.variation_attribute_value else None,
            'price': self.latest_price.sp.__float__() if self.latest_price else None,
            'mrp': self.latest_price.mrp.__float__() if self.latest_price else None,
            'total_stocks': self.total_stocks,
            'thumbnail_url': self.thumbnail_url,
            'images': [image.as_dict for image in self.images],
            'sku': self.sku,
            'attributes': [attribute.as_dict for attribute in self.attributes],
            'status': self.status,
            'tags': [value.strip() for value in self.tags.split(',')] if self.tags else None,
            'slung': self.slung,
            'reviews': [review.as_dict_min for review in self.latest_reviews],
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the min dict of product
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'store': self.store.id,
            'parent': self.parent.id if self.parent else None,
            'name': self.name,
            'description': self.description,
            'category': self.category.as_dict_min,
            'brand': self.brand.as_dict_min,
            'variation_attribute': self.variation_attribute.as_dict_min if self.variation_attribute else None,
            'variation_attribute_value': self.variation_attribute_value.as_dict_min if self.variation_attribute_value else None,
            'price': self.latest_price.sp.__float__() if self.latest_price else None,
            'mrp': self.latest_price.mrp.__float__() if self.latest_price else None,
            'total_stocks': self.total_stocks,
            'thumbnail_url': self.thumbnail_url,
            'images': [image.as_dict_min for image in self.images],
            'sku': self.sku,
            'attributes': [attribute.as_dict_min for attribute in self.attributes],
            'status': self.status,
            'tags': [value.strip() for value in self.tags.split(',')] if self.tags else None,
            'slung': self.slung,
            'reviews': [review.as_dict_min for review in self.latest_reviews],
            'is_active': self.is_active,
            'is_approved': self.is_approved,
        }

    # Property to get the dict of product with child
    @property
    def as_dict_with_child(self):
        return {
            'id': self.id,
            'store': self.store.id,
            'parent': self.parent.id if self.parent else None,
            'name': self.name,
            'description': self.description,
            'category': self.category.as_dict_min,
            'brand': self.brand.as_dict_min,
            'variation_attribute': self.variation_attribute.as_dict if self.variation_attribute else None,
            'variation_attribute_value': self.variation_attribute_value.as_dict_min if self.variation_attribute_value else None,
            'price': self.latest_price.sp.__float__() if self.latest_price else None,
            'mrp': self.latest_price.mrp.__float__() if self.latest_price else None,
            'total_stocks': self.total_stocks,
            'thumbnail_url': self.thumbnail_url,
            'images': [image.as_dict_min for image in self.images],
            'sku': self.sku,
            'attributes': [attribute.as_dict_min for attribute in self.attributes],
            'children': [child.as_dict_min for child in self.children.all()],
            'status': self.status,
            'tags': [value.strip() for value in self.tags.split(',')] if self.tags else None,
            'slung': self.slung,
            'reviews': [review.as_dict_min for review in self.latest_reviews],
            'is_active': self.is_active,
            'is_approved': self.is_approved,
        }

    # Property to get the dict of base product
    @property
    def as_dict_base(self):
        return {
            'id': self.id,
            'store': self.store.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.as_dict_min,
            'brand': self.brand.as_dict_min,
            'total_variants': self.children.count(),
            'thumbnail_url': self.children.first().thumbnail_url if self.children.exists() else None,
            'sku': self.sku,
            'status': self.status,
            'tags': [value.strip() for value in self.tags.split(',')] if self.tags else None,
            'slung': self.slung,
            'ratings': self.average_rating.__float__(),
            'reviews_count': self.product_reviews.count(),
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the dict of base product for customer
    @property
    def as_dict_base_min(self):
        return {
            'id': self.id,
            'store': self.store.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.as_dict_min,
            'brand': self.brand.as_dict_min,
            'total_variants': self.children.count(),
            'thumbnail_url': self.children.first().thumbnail_url if self.children.exists() else None,
            'sku': self.sku,
            'slung': self.slung,
            'ratings': self.average_rating.__float__(),
            'reviews_count': self.product_reviews.count(),
        }

    # Property to get the dict of base product with child
    @property
    def as_dict_base_with_child(self):
        return {
            'id': self.id,
            'store': self.store.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.as_dict_min,
            'brand': self.brand.as_dict_min,
            'thumbnail_url': self.children.first().thumbnail_url if self.children.exists() else None,
            'sku': self.sku,
            'status': self.status,
            'tags': [value.strip() for value in self.tags.split(',')] if self.tags else None,
            'children': [child.as_dict for child in self.children.all()],
            'slung': self.slung,
            'ratings': self.average_rating.__float__(),
            'reviews_count': self.product_reviews.count(),
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    # Property to get the dict of base product with child min
    @property
    def as_dict_base_with_child_min(self):
        return {
            'id': self.id,
            'store': self.store.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.as_dict_min,
            'brand': self.brand.as_dict_min,
            'thumbnail_url': self.children.first().thumbnail_url if self.children.exists() else None,
            'sku': self.sku,
            'children': [child.as_dict_min for child in self.children.all()],
            'slung': self.slung,
            'ratings': self.average_rating.__float__(),
            'reviews_count': self.product_reviews.count(),
        }


# ----------------------------------@mit----------------------------------
# Product Price Model
class ProductPrice(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_prices')
    sp = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Price'
        verbose_name_plural = 'Product Prices'

    def __str__(self):
        return f'{self.product.name} - {self.sp}'

    # Property to get dict of product price
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'product': self.product.id,
            'price': self.sp.__float__(),
            'mrp': self.mrp.__float__(),
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get min dict of product price
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'product': self.product.id,
            'price': self.sp.__float__(),
            'mrp': self.mrp.__float__(),
            'is_active': self.is_active,
        }


# ----------------------------------@mit----------------------------------
# Product Stock Model
class ProductStock(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_stocks')
    quantity = models.IntegerField()
    remarks = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Stock'
        verbose_name_plural = 'Product Stocks'

    def __str__(self):
        return self.quantity.__str__()

    # Property for status of product stock
    @property
    def status(self):
        return 'Increment' if self.quantity > 0 else 'Decrement'

    # Property to get the dict of product stock
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'status': self.status,
            'remarks': self.remarks,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the min dict of product stock
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'status': self.status,
            'remarks': self.remarks,
            'quantity': self.quantity,
        }


# ----------------------------------@mit----------------------------------
# Product Image Model
class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_images')
    image = models.FileField(upload_to='assets/product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return self.image.url if self.image else ''

    # Property to get the image url
    @property
    def image_url(self):
        return self.image.url if self.image else None

    # Property to get the dict of product image
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'url': self.image_url,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the min dict of product image
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'url': self.image_url,
        }


# ----------------------------------@mit----------------------------------
# Product Attribute Model
class ProductAttribute(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_attributes')
    attribute = models.ForeignKey('Attribute', on_delete=models.CASCADE, related_name='product_attributes')
    value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Attribute'
        verbose_name_plural = 'Product Attributes'

    def __str__(self):
        return self.value

    # Property to get the dict of product attribute
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'attribute': self.attribute.as_dict_min,
            'value': self.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the min dict of product attribute
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'attribute': self.attribute.as_dict_min,
            'value': self.value,
        }


# ----------------------------------@mit----------------------------------
# Brand Model
class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='assets/brand_images/', blank=True, null=True)
    category = models.ForeignKey('common.Category', on_delete=models.PROTECT, related_name='brands')
    store = models.ForeignKey('store.Store', on_delete=models.PROTECT, related_name='brands', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name

    # Property to get the image url
    @property
    def image_url(self):
        return self.image.url if self.image else None

    # Property to get the total products of brand
    @property
    def total_products(self):
        return self.products.count()

    # Property to get the total stores of brand
    @property
    def total_stores(self):
        return self.products.values_list('store', flat=True).distinct().count()

    # Property to get the dict of brand
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.image_url,
            'category': self.category.as_dict_min,
            'added_by': {'id': self.store.id, 'name': self.store.name} if self.store else None,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the min dict of brand
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.image_url,
        }

    # Property to get the dict of brand details
    @property
    def as_dict_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.image_url,
            'category': self.category.as_dict_min,
            'added_by': self.store.as_dict_min if self.store else None,
            'total_products': self.total_products,
            'total_stores': self.total_stores,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


# ----------------------------------@mit----------------------------------
# ProductReview Model
class ProductReview(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_reviews')
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.DecimalField(default=1.0, max_digits=2, decimal_places=1)
    comment = models.TextField(max_length=520, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'

    def __str__(self):
        return self.comment

    # Property to get all images
    @property
    def images(self):
        return self.review_images.all()

    # Property to get the dict of product review
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'product': self.product.as_dict_min,
            'customer': self.customer.as_dict_min,
            'rating': self.rating.__float__(),
            'comment': self.comment,
            'images': [image.as_dict for image in self.images],
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Property to get the min dict of product review
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'customer': self.customer.as_dict_min,
            'rating': self.rating.__float__(),
            'comment': self.comment,
            'images': [image.as_dict for image in self.images],
            'created_at': self.created_at
        }


# ----------------------------------@mit----------------------------------
# Product Review Image Model
class ProductReviewImage(models.Model):
    review = models.ForeignKey('ProductReview', on_delete=models.CASCADE, related_name='review_images')
    image = models.FileField(upload_to='assets/product_review_images/', blank=True, null=True)

    # Property to get image url
    @property
    def image_url(self):
        return self.image.url if self.image else None

    # Property to get the dict of product review image
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'url': self.image.url,
        }

    class Meta:
        verbose_name = 'Product Review Image'
        verbose_name_plural = 'Product Review Image'

    def __str__(self):
        return self.image_url
