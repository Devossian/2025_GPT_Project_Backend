import json
from chat.models import ChatRoom
import tiktoken

MAX_TOKENS = 4096  # GPT-4 기준 최대 컨텍스트 길이
SUMMARIZE_THRESHOLD = 3000  # 3000 토큰을 초과하면 요약 실행

def add_message_to_history(room: ChatRoom, role: str, content: str) -> None:
    # history를 list로 파싱
    history_list = get_history(room)
    
    # 메시지 객체 생성
    new_msg = {"role": role, "content": content}
    
    # list에 append
    history_list.append(new_msg)
    
    # 토큰 수 계산해서 초과 시 요약
    history_list = trim_history_if_needed(history_list)

    # 다시 JSON 문자열로 직렬화 후 room.history에 저장
    room.history = json.dumps(history_list, ensure_ascii=False)
    room.save()


def get_history(room: ChatRoom):
    try:
        history_list = json.loads(room.history)
        if not isinstance(history_list, list):
            history_list = []
    except (json.JSONDecodeError, TypeError):
        history_list = []
    
    return history_list


def count_tokens(messages, model="gpt-4"):
    """ 대화 메시지 리스트의 총 토큰 개수를 계산하는 함수 """
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for msg in messages:
        num_tokens += len(encoding.encode(msg["content"]))  # content를 토큰으로 변환
    return num_tokens


def trim_history_if_needed(history_list: list):
    """ 과거 채팅 토큰 수 초과시 가장 오래된 채팅 망각 """
    while count_tokens(history_list) > SUMMARIZE_THRESHOLD:
        history_list.pop(0)
    return history_list