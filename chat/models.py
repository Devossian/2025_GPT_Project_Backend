from django.db import models, transaction
from django.utils.timezone import now
from account.models import CustomUser
import uuid

# 채팅방 모델
class ChatRoom(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ChatRoom")
    roomid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)  # 전세계적으로 고유한 UUID
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True)
    messages = models.IntegerField(default=0)
    history = models.TextField(null=True)

    def __str__(self):
        return f"{self.roomid},{self.name},{self.created_at},{self.timestamp},{self.messages}"
    
# 채팅 메시지 모델
class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="message")
    senderid = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # 레코드가 생성될 때 ChatRoom 레코드에 메세지 수 및 최종 수정 시간 기록
    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:  # 새로 생성된 메시지일 경우(아직 레코드에 존재하지 않는 경우)에만 실행
                # 메시지를 저장
                super().save(*args, **kwargs)

                # FK ChatRoom의 timestamp를 현재 시간으로 업데이트
                self.room.timestamp = now()
                self.room.messages = self.room.messages + 1 # 메시지 카운트 증가
                self.room.save()
            else:
                super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.senderid},{self.room.name},{self.content[:20]},{self.timestamp}"