from django.urls import path
from . import views
from allauth.socialaccount.providers.google.views import oauth2_login as google_login_view
from allauth.socialaccount.providers.facebook.views import oauth2_login as facebook_login_view
from allauth.socialaccount.providers.github.views import oauth2_login as github_login_view

urlpatterns = [
    path('', views.login, name='login_page'),
    path('home/', views.homepage, name='home'),
    path('apply-effect/', views.apply_image_effect, name='apply_effect'),
    path('save/', views.save_image, name='save_image'),
    path('delete/<int:image_id>/', views.delete_image, name='delete_image'),
    path('share/<int:image_id>/', views.share_image, name='share_image'),
    path('api/overview', views.api_overview, name='api_overview'),

    # Direct social login URLs
    path('accounts/google/login/', google_login_view, name='google_login'),
    path('accounts/facebook/login/', facebook_login_view, name='facebook_login'),
    path('accounts/github/login/', github_login_view, name='github_login'),
]
