from enum import Enum


class TTSInputMapping(str, Enum):
    MAKE_HEART = "사랑해"
    MAKE_HUG = "안아줄게"
    MAKE_HELLO = "안녕"
    SCISSORS = "가위!"
    ROCK = "바위!"
    PAPER = "보!"
    GOOD_MORNING = "좋은 아침!"
    GOOD_NIGHT = "잘자요~"
    ATE_ALL = "이 닦을 시간이야~"
    HUNGRY = "밥 먹을 시간이야~"
    INIT_POSE = "초기 자세로 이동할게"


# Command Enum을 TTSInputMapping 변환하는 함수
def get_text_from_command(command: str) -> str:
    mapping = {
        "make_heart": TTSInputMapping.MAKE_HEART.value,
        "make_hug": TTSInputMapping.MAKE_HUG.value,
        "make_hello": TTSInputMapping.MAKE_HELLO.value,
        "scissors": TTSInputMapping.SCISSORS.value,
        "rock": TTSInputMapping.ROCK.value,
        "paper": TTSInputMapping.PAPER.value,
        "good_morning": TTSInputMapping.GOOD_MORNING.value,
        "good_night": TTSInputMapping.GOOD_NIGHT.value,
        "ate_all": TTSInputMapping.ATE_ALL.value,
        "hungry": TTSInputMapping.HUNGRY.value,
        "init_pose": TTSInputMapping.INIT_POSE.value,
    }
    temp = mapping.get(command, None)

    return temp if temp is not None else command


def match_stt_to_tts_response(stt_text: str) -> tuple[str | None, str | None]:
    stt_lower = stt_text.lower().strip()
    keyword_mapping = {
        # 감정 표현
        ("사랑", "좋아", "러브"): (TTSInputMapping.MAKE_HEART.value, "make_heart"),
        ("안아", "포옹", "허그"): (TTSInputMapping.MAKE_HUG.value, "make_hug"),
        ("안녕", "하이", "헬로", "반가워"): (
            TTSInputMapping.MAKE_HELLO.value,
            "make_hello",
        ),
        ("가위",): (TTSInputMapping.SCISSORS.value, "scissors"),
        ("바위",): (TTSInputMapping.ROCK.value, "rock"),
        ("보",): (TTSInputMapping.PAPER.value, "paper"),
        ("좋은 아침", "굿모닝", "아침"): (
            TTSInputMapping.GOOD_MORNING.value,
            "good_morning",
        ),
        ("잘자", "굿나잇", "밤", "자요"): (
            TTSInputMapping.GOOD_NIGHT.value,
            "good_night",
        ),
        ("이", "양치", "닦", "다 먹"): (TTSInputMapping.ATE_ALL.value, "ate_all"),
        ("배고", "밥", "식사", "먹"): (TTSInputMapping.HUNGRY.value, "hungry"),
        ("초기", "원위치", "돌아가"): (TTSInputMapping.INIT_POSE.value, "init_pose"),
    }

    for keywords, (reponse, command) in keyword_mapping.items():
        if any(keyword in stt_lower for keyword in keywords):
            return reponse, command

    return None, None
