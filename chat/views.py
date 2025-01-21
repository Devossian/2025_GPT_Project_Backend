from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import serializers
from .models import ChatRoom

# 시리얼라이저
class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['user', 'roomid', 'name', 'created_at', 'timestamp', 'messages']

class ChatRoomAPI(APIView):
    def get(self, request):
        query_params = request.query_params
        userid = query_params.get('userid')
        print(userid)
        
        if not userid:
            return JsonResponse({"error":"userid가 필요합니다."}, status=400)

        chatrooms = ChatRoom.objects.filter(user = userid).order_by('timestamp')
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return JsonResponse({'rooms':serializer.data})