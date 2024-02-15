from django.urls import path, include

from api.v1.common import views as common_views
from .a_views import a_get_views, a_add_views, a_update_views

urlpatterns = [
    path('category/', include([
        path('<int:category_id>', common_views.get_category, name='get_category'),
        path('list', common_views.get_product_categories, name='get_category_list'),
        path('add', common_views.add_category, name='add_category'),
        path('update/<int:category_id>', common_views.update_category, name='update_category'),
    ])),
    path('brand/', include([
        path('<int:brand_id>', a_get_views.get_brand, name='brand'),
        path('list', a_get_views.get_brands, name='brands'),
        path('add', a_add_views.add_brand, name='add_brand'),
        path('update/<int:brand_id>', a_update_views.update_brand, name='update_brand'),
    ])),
    path('attribute/', include([
        path('<int:attribute_id>', a_get_views.get_attribute, name='attribute'),
        path('list', a_get_views.get_attributes, name='attributes'),
        path('add', a_add_views.add_attribute, name='add_attribute'),
        path('update/<int:attribute_id>', a_update_views.update_attribute, name='update_attribute'),
    ])),
    path('variation-attribute/', include([
        path('<int:variation_attribute_id>', a_get_views.get_variation_attribute, name='variation_attribute'),
        path('list', a_get_views.get_variation_attributes, name='variation_attributes'),
        path('add', a_add_views.add_variation_attribute, name='add_variation_attribute'),
        path('update/<int:variation_attribute_id>', a_update_views.update_variation_attribute,
             name='update_variation_attribute'),
    ])),
    path('variation-attribute-value/', include([
        path('<int:variation_attribute_value_id>', a_get_views.get_variation_attribute_value,
             name='variation_attribute_value'),
        path('list', a_get_views.get_variation_attribute_values, name='variation_attribute_values'),
        path('add', a_add_views.add_variation_attribute_value, name='add_variation_attribute_value'),
        path('update/<int:variation_attribute_value_id>', a_update_views.update_variation_attribute_value,
             name='update_variation_attribute_value'),
    ])),
    path('product/', include([
        path('<int:product_id>', a_get_views.get_product, name='product'),
        path('list', a_get_views.get_products, name='products'),
        path('add', a_add_views.add_product, name='add_product'),
        # path('update/<int:product_id>', a_update_views.update_product, name='update_product'),
        path('review/', include([
            # path('<int:review_id>', a_get_views.get_product_review, name='product_review'),
            # path('list', a_get_views.get_product_reviews, name='product_reviews'),
            path('add', a_add_views.add_product_review, name='add_product_review'),
        ]), name='review'),
    ])),
    path('product-attribute/', include([
        path('<int:product_attribute_id>', a_get_views.get_product_attribute, name='product_attribute'),
        path('list', a_get_views.get_product_attributes, name='product_attributes'),
        path('add', a_add_views.add_product_attribute, name='add_product_attribute'),
        path('update/<int:product_attribute_id>', a_update_views.update_product_attribute,
             name='update_product_attribute'),
    ])),
    path('product-price/', include([
        path('<int:product_price_id>', a_get_views.get_product_price, name='product_price'),
        path('list', a_get_views.get_product_prices, name='product_prices'),
        path('add', a_add_views.add_product_price, name='add_product_price'),
        path('update/<int:product_price_id>', a_update_views.update_product_price, name='update_product_price'),
    ])),
    path('product-stock/', include([
        path('<int:product_stock_id>', a_get_views.get_product_stock, name='product_stock'),
        path('list', a_get_views.get_product_stocks, name='product_stocks'),
        path('add', a_add_views.add_product_stock, name='add_product_stock'),
        path('update/<int:product_stock_id>', a_update_views.update_product_stock, name='update_product_stock'),
    ])),
    path('product-image/', include([
        path('list', a_get_views.get_product_images, name='product_images'),
        path('add', a_add_views.add_product_image, name='add_product_image'),
    ])),
    path('search-products', a_get_views.search_products, name='search_products'),
]
