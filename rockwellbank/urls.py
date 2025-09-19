from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about'),
    path('signin/', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('portfolio/', views.portfolio, name = 'portfolio'),
    path('transfer/', views.transfer, name = 'transfer'),
    path('profile/', views.profile_io, name='profile'),
    path('deposit-checks/', views.contact_us, name='contactus'),
    path('transfer-progress/<int:transaction_id>/', views.transfer_progress, name='transfer_progress'),
    path('transfer/imf-verification/<int:transaction_id>/', views.imf_verification, name='imf_verification'),
    path('stocks-investment/', views.my_cards, name='mycards'),
    path('transaction/<int:transaction_id>/download/', views.download_receipt_pdf, name='download_receipt'),
    path('logout', views.logout, name = 'logout'),
    
      
]
