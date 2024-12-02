from django.urls import path
from . import views 

urlpatterns = [
    path('<int:room_id>/send-messages/', views.SendMessageView.as_view(), name='send_message'),
    path('<int:room_id>/messages/', views.GetMessagesView.as_view(), name='get_messages'),
    path('<int:room_id>/share/', views.ShareFileView.as_view(), name='share_file'),
]
