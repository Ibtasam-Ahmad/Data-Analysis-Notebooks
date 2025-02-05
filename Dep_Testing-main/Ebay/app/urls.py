from django.urls import path
from .views import (SearchAndDownloadImages, ScrapeEbay, ManageImagePaths,

                        ProductListView,
                        ProductDetailView,
                        ProductCreateView,
                        ProductDeleteView,
                        ProductUpdateView
)
from . import views



urlpatterns = [
    path('scrape-ebay/', ScrapeEbay.as_view(), name='scrape_ebay'),
    path('search-and-download/', SearchAndDownloadImages.as_view(), name='search_and_download'),
    path('manage-image-paths/', ManageImagePaths.as_view(), name='manage_image_paths'),


    path('product/', ProductListView.as_view(), name='get-all-products'),

    path('product/<str:ebay_id>/', ProductDetailView.as_view(), name='get-product-detail-by-ebay-id'),
    
    
    path('products/create/', ProductCreateView.as_view(), name='create-product'),

    
    path('products/delete/<str:ebay_id>/', ProductDeleteView.as_view(), name='delete-product-by-ebay-id'),
    
    
    path('product/update/<str:ebay_id>/', ProductUpdateView.as_view(), name='update-product-by-ebay-id'),

    
    path('predict/<int:ebay_id>/', views.get_predicted_prices, name='get_predicted_prices'),

]
