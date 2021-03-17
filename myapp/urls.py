from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('about/',views.about,name='AboutUs'),
    path('contact/',views.contact,name='contactUs'),
    path('checkout/',views.checkout,name='Checkout'),
    path('tracker/',views.tracker,name='TrackingStatus'),
    path('cancelorder/',views.cancelorder,name='CancelOrder'),
    path('search/',views.search,name='Search'),
    path('products/<int:myid>',views.prodView,name='ProductView'),
    path('handlerequest/',views.handlerequest,name='HandleRequest'),


]