from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import serializers
from .models import ChatRoom, ChatMessage

# 시리얼라이저
class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['roomid', 'name', 'created_at', 'timestamp', 'messages']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['senderid', 'content', 'timestamp']
    
class ChatRoomAPI(APIView):
    def get(self, request):
        query_params = request.query_params
        userid = query_params.get('userid')
        print(userid) # 디버깅용
        
        if not userid:
            return JsonResponse({"error":"userid가 필요합니다."}, status=400)

        # 채팅방 목록 받아오기
        chatrooms = ChatRoom.objects.filter(user = userid).order_by('timestamp')
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return JsonResponse({'rooms':serializer.data})
    
class ChatAPI(APIView):
    def get(self, request):
        query_params = request.query_params
        roomid = query_params.get('roomid')
        print(roomid) # 디버깅용

        if not roomid:
            return JsonResponse({"error":"roomid가 필요합니다."}, status=400)
        
        # 메시지 목록 받아오기
        chatroom = ChatRoom.objects.get(roomid=roomid)
        messages = chatroom.message.all().order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        print(serializer.data)
        return JsonResponse({'messages':serializer.data})
