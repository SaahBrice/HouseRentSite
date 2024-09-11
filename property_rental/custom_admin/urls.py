from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('site-parameters/', views.site_parameters, name='site_parameters'),
    path('<str:model_name>/', views.model_list, name='model_list'),
    path('<str:model_name>/create/', views.model_create, name='model_create'),
    path('<str:model_name>/<int:pk>/update/', views.model_update, name='model_update'),
    path('<str:model_name>/<int:pk>/delete/', views.model_delete, name='model_delete'),
]