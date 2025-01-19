from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from .api_key_manager import acquire_api_key, release_api_key
import openai

class PostGPTAPI(APIView): # 
    def post(self, request):
        data = json.loads(request.body)
        userid = data.get('userid')
        message  = data.get('message')
        model = data.get('model')

        # 데이터 누락시 400에러
        if not userid or not message or not model:
            return JsonResponse({'status': 'error', 'message': 'username and message are required'}, status=400)
        
        # api 키 습득
        api_key = acquire_api_key()
        

        # api_key 누락시 429에러(모든 API 키 사용중)
        if not api_key:
            return JsonResponse({'error': 'All API keys are currently in use.'}, status=429)
        
        try:
            # gpt api 호출
            print(api_key)
            client = openai
            client.api_key = api_key
            print(api_key) 
            
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ]
            )

            gpt_answer = completion.choices[0].message

            return Response({
                'status': 'success',
                'answer': gpt_answer.content.strip(),
            })
        except Exception as e:
            return JsonResponse({"status": "Error", "answer": str(e)}, status=400)
        finally:
            # 사용한 api 키 반환
            release_api_key(api_key)