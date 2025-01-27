from django.shortcuts import render
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, ChatMessage
from account.models import CustomUser
import json

# 시리얼라이저
class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['roomid', 'name', 'created_at', 'timestamp', 'messages']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['senderid', 'content', 'timestamp']
    
# 채팅방 조회 API
class ChatRoomAPI(APIView):
    def get(self, request):
        query_params = request.query_params
        userid = query_params.get('userid')
        
        if not userid:
            return Response({"error":"userid가 필요합니다."}, status=400)

        # 채팅방 목록 받아오기
        chatrooms = ChatRoom.objects.filter(user = userid).order_by('timestamp')
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return Response({'rooms':serializer.data}, status=200)
    
# 채팅 이력 조회 API
class ChatMessagesAPI(APIView):
    def get(self, request):
        query_params = request.query_params
        roomid = query_params.get('roomid')

        if not roomid:
            return Response({"error":"roomid가 필요합니다."}, status=400)
        
        # 메시지 목록 받아오기
        chatroom = get_object_or_404(ChatRoom, roomid=roomid)
        messages = chatroom.message.all().order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response({'messages':serializer.data}, status=200)

# 채팅방 삭제 API
class RemoveChatRoomAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, roomid=None):
        try:
            room = ChatRoom.objects.get(roomid=roomid)
            # 해당 채팅방 유저인지 확인
            if request.user != room.user:
                return Response({'error': '해당 채팅방을 삭제할 권한이 없습니다.'}, status=403)
            
            room.delete()
            return Response({'message': 'Room이 성공적으로 삭제되었습니다.'}, status=200)
        except ChatRoom.DoesNotExist:
            return Response({'error':'요청하신 room이 존재하지 않습니다.'}, status=404)
        except Exception as e:
            return Response({'error':str(e)}, status=400)

# 채팅방 생성 API
class CreateChatRoomAPI(APIView):
    def post(self, request):
        data = request.data

        userid = data.get('userid')
        room_name = data.get('room_name','Untitled Room')
        try:
            user = CustomUser.objects.get(id = userid)
            room = ChatRoom.objects.create(user=user, name=room_name)
            return Response({'message':'성공적으로 Room이 생성됐습니다.', 'roomid':str(room.roomid)}, status=201)
        except CustomUser.DoesNotExist:
            return Response({'error':'해당 userid를 가진 user가 없습니다.'}, status=404)
        except Exception as e:
            return Response({'error':str(e)}, status=500)