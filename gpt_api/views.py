from django.shortcuts import render
from django.conf import settings
from django.db import transaction
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from account.models import CustomUser
from chat.models import ChatMessage, ChatRoom
from .api_key_manager import acquire_api_key, release_api_key
from .history_manager import get_history, add_message_to_history
from statistic.models import UsageRecord
import openai
import time
import itertools

class PostGPTAPI(APIView): # 
    def post(self, request):
        data = json.loads(request.body)
        message  = data.get('message')
        model = data.get('model')
        # 채팅방 정보 받기
        roomid = data.get('roomid')
        room = ChatRoom.objects.get(roomid=roomid)
        # 그리고 유저 찾기
        userid = request.user.id
        timestamp = time.time()

        # 데이터 누락시 400에러
        if not userid or not message or not model:
            return Response({'message': '누락된 parameter가 있습니다.'}, status=400)
        
        # 채팅 송신 기록 남기기
        chatmessage = ChatMessage.objects.create(room=room, content=message, senderid=userid, timestamp=timestamp)
        chatmessage.save()
        
        # api 키 습득
        api_key = acquire_api_key()
        
        # api_key 누락시 429에러(모든 API 키 사용중)
        if not api_key:
            return Response({'message': '모든 키가 사용중입니다.'}, status=429)
        
        try:
            # 트랜잭션 원자성 보장
            with transaction.atomic():
                # 유저 검색
                user = CustomUser.objects.select_for_update(skip_locked=True).get(id=userid) # 사용 모델 LOCK

                # 잔고 확인
                if user.balance < settings.MODEL_COST[model]:
                    return Response({'message': '잔고가 부족합니다.'}, status=403)
                
                # 채팅 기억 불러오기
                messages = list(itertools.chain(
                    [{"role": "system", "content": "You are a helpful assistant."}],
                    get_history(room=room),
                    [{"role": "user", "content": message}]
                ))
                
                # gpt api 호출
                client = openai
                client.api_key = api_key
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                gpt_answer = completion.choices[0].message.content.strip()

                # 채팅 수신 기록 남기기
                chatmessage = ChatMessage.objects.create(room=room, content=gpt_answer, senderid=0, timestamp=timestamp)
                chatmessage.save()

                # 채팅 기억 기록
                add_message_to_history(room=room, role="user", content=message)
                add_message_to_history(room=room, role="assistant", content=gpt_answer)

                # 잔고 차감
                user.balance = user.balance - settings.MODEL_COST[model]
                user.save()

                # 사용 내역 저장
                usage_record = UsageRecord.objects.create(user=user, used_model=model, cost=settings.MODEL_COST[model])
                usage_record.save()

                return Response({
                    'message': gpt_answer
                }, status=200)
        # 유저를 찾을 수 없는 경우
        except CustomUser.DoesNotExist:
            return Response({'message': '유저를 찾을 수 없습니다.'}, status=404)
        # openai Authentication error 발생시
        except openai.AuthenticationError:
            return Response({'message': 'API 요청중 문제가 생겼습니다. 잔고는 차감되지 않습니다.'}, status=401)
        # openai rate limit reached 발생시
        except openai.RateLimitError:
            return Response({'message': '사용자가 많아 요청이 거절됐습니다. 잔고는 차감되지 않습니다.'}, status=429)
        # 트랜젝션 문제거나, gpt api 호출에 문제가 생긴 경우
        except Exception as e:
            return Response({"message": str(e)}, status=400)
        finally:
            # 사용한 api 키 반환
            release_api_key(api_key)