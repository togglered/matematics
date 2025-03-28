from django.urls import path
from . import views


app_name = 'users'


urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('statistics/', views.statistics, name='statistics'),
    path('favorites/', views.favorites, name='favorites'),
    path('verification/<str:verification_token>/', views.verification, name='verification'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('set-new-pass/<str:verification_token>/', views.set_new_pass, name='set_new_pass'),
    path('get-proof-link/', views.get_proof_link, name='get_proof_link'),
]
