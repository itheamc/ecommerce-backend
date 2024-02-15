from django.urls import path, include
from .catalogue import urls as catalogue_urls
from .store import urls as store_urls
from .customer import urls as customer_urls
from .common import urls as common_urls
from .utils import urls as utils_urls

urlpatterns = [
    path('catalogue/', include(catalogue_urls)),
    path('store/', include(store_urls)),
    path('customer/', include(customer_urls)),
    path('common/', include(common_urls)),
    path('utils/', include(utils_urls)),
]
