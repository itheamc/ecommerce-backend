from django.contrib import admin
from .models import *


# ----------------------------------@mit----------------------------------
# Model Admins
# ------------------------------------------------------------------------

# Admin for Attribute
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'is_active',)
    list_filter = ('category', 'is_active',)
    search_fields = ('name',)


# Admin for Variation Attribute
class VariationAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'category', 'is_active',)
    list_filter = ('category', 'is_active',)
    search_fields = ('name', 'description',)


# Admin for VariationAttributeValue
class VariationAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'variation_attribute', 'value',)
    list_filter = ('variation_attribute',)
    search_fields = ('variation_attribute', 'value',)


# Admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'name', 'description', 'parent', 'category', 'brand', 'is_active', 'is_approved',)
    list_filter = ('is_active', 'is_approved',)
    search_fields = ('name', 'description', 'store', 'category',)


# Admin for ProductPrice
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'sp', 'mrp', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('product',)


# Admin for ProductStock
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'remarks',)
    list_filter = ('product',)
    search_fields = ('product',)


# Admin for ProductImage
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image_url', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('product',)


# Admin for ProductAttribute
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'attribute', 'value',)
    list_filter = ('product', 'attribute',)
    search_fields = ('product', 'attribute', 'value',)


# Admin for Brand
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'category', 'store', 'is_active',)
    list_filter = ('is_active', 'category',)
    search_fields = ('name', 'description',)


# Admin for Product Review
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'customer', 'rating', 'comment',)
    list_filter = ('product', 'customer',)
    search_fields = ('product', 'customer',)


# Admin for Product Review Image
class ProductReviewImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'image_url',)
    list_filter = ('review',)
    search_fields = ('review',)


# ----------------------------------@mit----------------------------------
# Registering the models
# ------------------------------------------------------------------------

admin.site.register(Attribute, AttributeAdmin)
admin.site.register(VariationAttribute, VariationAttributeAdmin)
admin.site.register(VariationAttributeValue, VariationAttributeValueAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductPrice, ProductPriceAdmin)
admin.site.register(ProductStock, ProductStockAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(ProductReviewImage, ProductReviewImageAdmin)
