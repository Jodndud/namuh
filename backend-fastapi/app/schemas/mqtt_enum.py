from enum import Enum


class MQTTCommand(str, Enum):
    CMD_INIT_POSE = "init_pose"  # 초기 자세로 이동
    CMD_MAKE_HEART = "make_heart"  # 하트 제스처
    CMD_MAKE_HUG = "make_hug"  # 포옹(허그) 제스처
    CMD_MAKE_HELLO = "make_hello"  # 안녕(손인사) 제스처
    CMD_SCISSORS = "scissors"  # 가위 제스처
    CMD_ROCK = "rock"  # 바위 제스처
    CMD_PAPER = "paper"  # 보 제스처
    CMD_GOOD_MORNING = "good_morning"  # 좋은 아침 제스처
    CMD_GOOD_NIGHT = "good_night"  # 잘 자요 제스처
    CMD_ATE_ALL = "ate_all"  # 다 먹었어 제스처
    CMD_HUNGRY = "hungry"  # 배고파 제스처
