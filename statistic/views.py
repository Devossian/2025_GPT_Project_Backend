from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from statistic.models import UsageRecord
from datetime import datetime

class UsageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = ['used_model','cost','created_time']

# Create your views here.
@extend_schema(
    summary="사용 기록 조회",
    description="로그인한 사용자의 GPT 모델 사용 내역을 조회합니다. 날짜 범위를 지정할 수 있습니다.",
    parameters=[
        OpenApiParameter(
            name="start-date",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            required=False,
            description="조회 시작 날짜 (ISO 8601 형식: YYYY-MM-DDTHH:MM:SS, 기본값: 2025-01-01T00:00:00)"
        ),
        OpenApiParameter(
            name="end-date",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            required=False,
            description="조회 종료 날짜 (ISO 8601 형식: YYYY-MM-DDTHH:MM:SS, 기본값: 오늘 날짜)"
        ),
    ],
    responses={
        200: UsageRecordSerializer(many=True),
        500: serializers.Serializer(
            {
                "error": serializers.CharField(help_text="서버 내부 오류 메시지"),
            }
        ),
    }
)
class CheckUsage(APIView):
    def get(self, request):
        query_params = request.query_params
        start_date = query_params.get('start-date', '2025-01-01T00:00:00')
        start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
        end_date = query_params.get('end-date')
        # end_date 안주어지면 오늘 날짜로
        if not end_date:
            end_datetime = datetime.now()
        else:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
        print(start_datetime, end_datetime)

        try:
            # 유저 정보 이용하여 사용량 레코드 조회(start_datetime과 end_datetime 사이)
            user = request.user
            records = user.record.filter(
                created_time__gte=start_datetime,
                created_time__lte=end_datetime
            ).order_by('created_time')
            serializer = UsageRecordSerializer(records, many=True)
            
            return Response({'records':serializer.data},status=200)
        except Exception as e:
            return Response({'error',str(e)}, status=500)