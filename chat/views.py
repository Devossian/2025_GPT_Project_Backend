from django.shortcuts import render
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
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
@extend_schema(
    summary="채팅방 목록 조회",
    description="현재 로그인된 사용자의 채팅방 목록을 조회합니다.",
    responses={
        200: inline_serializer(
            name="ChatRoomListResponse",
            fields={"rooms": ChatRoomSerializer(many=True)}
        ),
    }
)
class ChatRoomAPI(APIView):
    def get(self, request):
        query_params = request.query_params
        user = request.user
        roomid = query_params.get('roomid')

        # 채팅방 목록 받아오기
        chatrooms = ChatRoom.objects.filter(user = user, roomid=roomid).order_by('timestamp')
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return Response({'rooms':serializer.data}, status=200)
    
# 채팅 이력 조회 API
@extend_schema(
    summary="채팅 메시지 조회",
    description="채팅방의 메시지 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="roomid",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            required=True,
            description="조회할 채팅방 ID"
        ),
    ],
    responses={
        200: inline_serializer(
            name="ChatMessagesResponse",
            fields={"messages": MessageSerializer(many=True)}
        ),
        400: inline_serializer(
            name="BadRequestResponse",
            fields={"error": serializers.CharField(help_text="오류 메시지")}
        ),
        404: inline_serializer(
            name="NotFoundResponse",
            fields={"error": serializers.CharField(help_text="채팅방을 찾을 수 없음")}
        ),
    }
)
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
@extend_schema(
    summary="채팅방 삭제",
    description="채팅방을 삭제합니다. 사용자는 자신이 생성한 채팅방만 삭제할 수 있습니다.",
    parameters=[
        OpenApiParameter(
            name="roomid",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            required=True,
            description="삭제할 채팅방 ID"
        ),
    ],
    responses={
        200: inline_serializer(
            name="DeleteChatRoomResponse",
            fields={"message": serializers.CharField(help_text="삭제 성공 메시지")}
        ),
        403: inline_serializer(
            name="ForbiddenResponse",
            fields={"error": serializers.CharField(help_text="삭제 권한 없음")}
        ),
        404: inline_serializer(
            name="NotFoundResponse",
            fields={"error": serializers.CharField(help_text="채팅방을 찾을 수 없음")}
        ),
    }
)
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
@extend_schema(
    summary="채팅방 생성",
    description="새로운 채팅방을 생성합니다.",
    request=inline_serializer(
        name="CreateChatRoomRequest",
        fields={
            "room_name": serializers.CharField(help_text="채팅방 이름", required=False, default="Untitled Room"),
        }
    ),
    responses={
        201: inline_serializer(
            name="CreateChatRoomResponse",
            fields={
                "message": serializers.CharField(help_text="생성 성공 메시지"),
                "roomid": serializers.UUIDField(help_text="생성된 채팅방 ID"),
            }
        ),
        404: inline_serializer(
            name="UserNotFoundResponse",
            fields={"error": serializers.CharField(help_text="사용자 정보 조회 실패")}
        ),
        500: inline_serializer(
            name="ServerErrorResponse",
            fields={"error": serializers.CharField(help_text="서버 내부 오류")}
        ),
    }
)
class CreateChatRoomAPI(APIView):
    def post(self, request):
        data = request.data

        room_name = data.get('room_name','Untitled Room')
        try:
            user = request.user
            room = ChatRoom.objects.create(user=user, name=room_name)
            return Response({'message':'성공적으로 Room이 생성됐습니다.', 'roomid':str(room.roomid)}, status=201)
        except CustomUser.DoesNotExist:
            return Response({'error':'회원정보를 조회 할 수 없습니다..'}, status=404)
        except Exception as e:
            return Response({'error':str(e)}, status=500)