from django.urls import path
from chat.views import ChatRoomAPI, ChatMessagesAPI, RemoveChatRoomAPI, CreateChatRoomAPI

urlpatterns = [
    path('lobby', ChatRoomAPI.as_view(), name='chat-room'),
    path('chat', ChatMessagesAPI.as_view(), name='chat'),
    path('remove-room/<str:roomid>', RemoveChatRoomAPI.as_view(), name='remove-room'),
    path('create-room',CreateChatRoomAPI.as_view(), name='create-chat-room'),
]