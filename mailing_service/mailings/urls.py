from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('recipients/', views.RecipientListView.as_view(), name='recipient_list'),
    path('recipients/add/', views.RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/edit/', views.RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', views.RecipientDeleteView.as_view(), name='recipient_delete'),
]