from django.urls import path
from chat.views import ChatRoomAPI, ChatMessagesAPI, RemoveChatRoomAPI

urlpatterns = [
    path('lobby/', ChatRoomAPI.as_view(), name='chat-room'),
    path('chat/', ChatMessagesAPI.as_view(), name='chat'),
    path('remove-room/', RemoveChatRoomAPI.as_view(), name='remove-room'),
]