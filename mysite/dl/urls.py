# from django.urls import path, reverse_lazy, reverse, include
from django.urls import path, reverse_lazy, include
from . import views
# from django.views.generic import TemplateView
# from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings



app_name = 'dl'
urlpatterns = [

    # path('', views.DlHomeView.as_view(), name='dl_home'),
    path('about/', views.DlAboutView.as_view(), name='dl_about'),
    path('signup/', views.signup, name='signup'),
    path('password/', views.change_password, name='change_password'),

    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    # url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #    views.activate, name='activate'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # path('images', views.ImageListView.as_view(), name='all'),

    path('', views.ImageListView.as_view(), name='all'),
    path('images/<int:pk>', views.ImageDetailView.as_view(), name='image_detail'),
    path('images/create', views.ImageCreateView.as_view(success_url=reverse_lazy('dl:all')), name='image_create'),
    path('images/<int:pk>/update', views.ImageUpdateView.as_view(success_url=reverse_lazy('dl:all')), name='image_update'),
    path('images/<int:pk>/delete', views.ImageDeleteView.as_view(success_url=reverse_lazy('dl:all')), name='image_delete'),

    path('categories/', views.CategoryListView.as_view(), name='all_categories'),
    path('categories/<int:pk>', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/create', views.CategoryCreateView.as_view(success_url=reverse_lazy('dl:all_categories')), name='category_create'),
    path('categories/<int:pk>/update', views.CategoryUpdateView.as_view(success_url=reverse_lazy('dl:all_categories')), name='category_update'),
    path('categories/<int:pk>/delete', views.CategoryDeleteView.as_view(success_url=reverse_lazy('dl:all_categories')), name='category_delete'),

    path('galleries/', views.GalleryListView.as_view(), name='all_galleries'),
    path('galleries/<int:pk>', views.GalleryDetailView.as_view(), name='gallery_detail'),
    path('galleries/create', views.GalleryCreateView.as_view(success_url=reverse_lazy('dl:all_galleries')), name='gallery_create'),
    path('galleries/<int:pk>/update', views.GalleryUpdateView.as_view(success_url=reverse_lazy('dl:all_galleries')), name='gallery_update'),
    path('galleries/<int:pk>/delete', views.GalleryDeleteView.as_view(success_url=reverse_lazy('dl:all_galleries')), name='gallery_delete'),

    path('orders/', views.OrderListView.as_view(), name='all_orders'),
    path('orders/<int:pk>', views.OrderDetailView.as_view(), name='order_detail'),

    path('stream_image/<int:pk>', views.stream_file, name='stream_image'),

    path('home/', views.HomeView.as_view(), name='home'),
    path('product/<pk>/', views.ProductView.as_view(), name='product'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', views.StripePaymentView.as_view(), name='stripe-payment'),
    path('add-to-cart/<pk>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', views.remove_from_cart, name='remove-from-cart'),
    path('reduce-quantity-item/<pk>/', views.reduce_quantity_item, name='reduce-quantity-item'),

    path('paypal/', include('paypal.standard.ipn.urls'), name='paypal-ipn'),
    path('paypal-form/', views.PaypalFormView.as_view(), name='paypal-form'),
    path('paypal-payment/', views.paypal_payment, name='paypal-payment' ),
    # path('payment/<payment_option>/', views.paypal_payment, name='paypal-payment'),
    path('paypal-return/', views.PaypalReturnView.as_view(), name='paypal-return'),
    path('paypal-cancel/', views.PaypalCancelView.as_view(), name='paypal-cancel'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),

    path('carousel/', views.CarouselView.as_view(), name='carousel'),

    path('contact/', views.contact_page, name='contact_page'),
    path('send_contact/', views.send_contact, name='send_contact'),

    path('user_list/', views.UserListView.as_view(), name='user_list'),
    path('products/', views.ProductListView.as_view(), name='all_products'),
    path('products/create', views.ProductCreateView.as_view(success_url=reverse_lazy('dl:all_products')), name='product_create'),
    path('products/<int:pk>/update', views.ProductUpdateView.as_view(success_url=reverse_lazy('dl:all_products')), name='product_update'),
    path('products/<int:pk>/delete', views.ProductDeleteView.as_view(success_url=reverse_lazy('dl:all_products')), name='product_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)