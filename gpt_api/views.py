from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
from django.db.models import F
from rest_framework.views import APIView
import json
from account.models import CustomUser
from .api_key_manager import acquire_api_key, release_api_key
import openai

class PostGPTAPI(APIView): # 
    def post(self, request):
        exceeded = False
        data = json.loads(request.body)
        userid = data.get('userid')
        message  = data.get('message')
        model = data.get('model')

        # 데이터 누락시 400에러
        if not userid or not message or not model:
            return JsonResponse({'message': 'username 또는 message가 누락되었습니다.'}, status=400) 
        
        # api 키 습득
        api_key = acquire_api_key()
        
        # api_key 누락시 429에러(모든 API 키 사용중)
        if not api_key:
            return JsonResponse({'message': '모든 키가 사용중입니다.'}, status=429)
        
        try:
            # 트랜잭션 원자성 보장
            with transaction.atomic():
                # 유저 검색
                user = CustomUser.objects.select_for_update().get(id=userid) # 사용 모델 LOCK
                print(user.username)

                # 잔고 확인
                if user.balance < settings.MODEL_COST[model]:
                    return JsonResponse({'message': '잔고가 부족합니다.'}, status=403)
                
                # gpt api 호출
                client = openai
                client.api_key = api_key
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": message}
                    ]
                )
                gpt_answer = completion.choices[0].message

                # 잔고 차감
                user.balance = user.balance - settings.MODEL_COST[model]
                user.save()

                return JsonResponse({
                    'message': gpt_answer.content.strip()
                }, status=200)
        # 유저를 찾을 수 없는 경우
        except CustomUser.DoesNotExist:
            return JsonResponse({'message': '유저를 찾을 수 없습니다.'}, status=404)
        # openai Authentication error 발생시
        except openai.AuthenticationError:
            return JsonResponse({'message': 'API 요청중 문제가 생겼습니다. 잔고는 차감되지 않습니다.'}, status=401)
        # openai rate limit reached 발생시
        except openai.RateLimitError:
            return JsonResponse({'message': '사용자가 많아 요청이 거절됐습니다. 잔고는 차감되지 않습니다.'}, status=429)
        # 트랜젝션 문제거나, gpt api 호출에 문제가 생긴 경우
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=400)
        finally:
            # 사용한 api 키 반환
            release_api_key(api_key)