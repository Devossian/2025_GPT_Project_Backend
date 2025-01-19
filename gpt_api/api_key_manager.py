import threading
import os


# env 폴더에 있는 API 키 목록 추출
OPENAI_API_KEY = os.getenv("OPENAI_API_KEYS")
api_keys = OPENAI_API_KEY.split(',')
api_keys = [key.strip() for key in api_keys]



# 사용할 API 키 목록과 해당 키의 사용 여부를 저장하는 전역 딕셔너리
API_KEYS_STATUS = {}
for key_val in api_keys:
    API_KEYS_STATUS[key_val] = False

# 멀티쓰레드 환경에서 동시 접근을 제어하기 위한 Lock
api_key_lock = threading.Lock()

def acquire_api_key():
    with api_key_lock:
        for key, in_use in API_KEYS_STATUS.items():
            if not in_use:
                API_KEYS_STATUS[key] = True
                return key
        return None  # 모든 키가 사용 중이면 None
    return None

def release_api_key(key):
    with api_key_lock:
        if key in API_KEYS_STATUS:
            API_KEYS_STATUS[key] = False
    return None
