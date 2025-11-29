from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('recipients/', views.RecipientListView.as_view(), name='recipient_list'),
    path('recipients/add/', views.RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/edit/', views.RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', views.RecipientDeleteView.as_view(), name='recipient_delete'),
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/add/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', views.MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/add/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', views.mailing_send, name='mailing_send'),
]