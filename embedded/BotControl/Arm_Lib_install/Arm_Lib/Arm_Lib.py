#!/usr/bin/env python3
# coding: utf-8
# import smbus
from time import sleep
import serial
import struct

# import threading


class Arm_Device(object):

    def __init__(self, com="/dev/myserial"):

        self.addr = 0x15
        self.__HEAD = 0xFF
        self.__DEVICE_ID = 0xFC
        self.__COMPLEMENT = 257 - self.__DEVICE_ID

        self.FUNC_UART_SERVO = 0x0A
        self.FUNC_UART_SUBS = 0x0B
        self.FUNC_UART_NUM = 0x22
        self.FUNC_UART_STATE = 0x33
        self.FUNC_UART_VERSION = 0x01
        self.FUNC_UART_result = 0x2A

        self.servo_H = 0
        self.servo_L = 0
        self.id = 0
        self.subs_H = 0
        self.subs_L = 0
        self.version = -1
        self.num = 0
        self.state = 0
        self.speech_state = 0

        self.ser = serial.Serial(com, 115200, timeout=0.2)
        sleep(0.2)

    # 데이터 프레임 타입에 따라 적절히 파싱
    def __parse_data(self, ext_type, ext_data):
        if ext_type == self.FUNC_UART_SERVO:
            self.servo_H = struct.unpack("B", bytearray(ext_data[0:1]))[0]
            self.servo_L = struct.unpack("B", bytearray(ext_data[1:2]))[0]
            self.id = struct.unpack("B", bytearray(ext_data[2:3]))[0]
        elif ext_type == self.FUNC_UART_SUBS:
            self.subs_H = struct.unpack("B", bytearray(ext_data[0:1]))[0]
            self.subs_L = struct.unpack("B", bytearray(ext_data[1:2]))[0]
        elif ext_type == self.FUNC_UART_NUM:
            self.num = struct.unpack("B", bytearray(ext_data[0:1]))[0]
        elif ext_type == self.FUNC_UART_VERSION:
            self.version = struct.unpack("B", bytearray(ext_data[0:1]))[0]
        elif ext_type == self.FUNC_UART_STATE:
            self.state = struct.unpack("B", bytearray(ext_data[0:1]))[0]
        elif ext_type == self.FUNC_UART_result:
            self.speech_state = struct.unpack("B", bytearray(ext_data[0:1]))[0]

    # 데이터 수신 receive data
    def __receive_data(self):
        head1 = bytearray(self.ser.read())[0]
        if head1 == self.__HEAD:
            head2 = bytearray(self.ser.read())[0]
            check_sum = 0
            rx_check_num = 0
            if head2 == self.__DEVICE_ID - 1:
                ext_len = bytearray(self.ser.read())[0]
                ext_type = bytearray(self.ser.read())[0]
                ext_data = []
                check_sum = ext_len + ext_type
                data_len = ext_len - 2
            while len(ext_data) < data_len:
                value = bytearray(self.ser.read())[0]
                ext_data.append(value)
                if len(ext_data) == data_len:
                    rx_check_num = value
                else:
                    check_sum = check_sum + value
            if check_sum % 256 == rx_check_num:
                self.__parse_data(ext_type, ext_data)
            else:
                print("check sum error:", ext_len, ext_type, ext_data)

    # 버스 서보 각도 설정 인터페이스: id: 1-6(0은 6개 서보 모두 제어) angle: 0-180 서보가 이동할 각도 설정
    def Arm_serial_servo_write(self, id, angle, time):
        sleep(0.01)
        if id == 0:  # 此为所有舵机控制
            self.Arm_serial_servo_write6(angle, angle, angle, angle, angle, angle, time)
        elif id == 2 or id == 3 or id == 4:  # 与实际相反角度
            angle = 180 - angle
            pos = int((3100 - 900) * (angle - 0) / (180 - 0) + 900)

            value_H = (pos >> 8) & 0xFF
            value_L = pos & 0xFF
            time_H = (time >> 8) & 0xFF
            time_L = time & 0xFF

            try:
                cmd = [0xFF, 0xFC, 0x07, 0x10 + id, value_H, value_L, time_H, time_L]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)

            except:
                print("Arm_serial_servo_write serial error")
        elif id == 5:
            pos = int((3700 - 380) * (angle - 0) / (270 - 0) + 380)

            value_H = (pos >> 8) & 0xFF
            value_L = pos & 0xFF
            time_H = (time >> 8) & 0xFF
            time_L = time & 0xFF
            try:
                cmd = [0xFF, 0xFC, 0x07, 0x10 + id, value_H, value_L, time_H, time_L]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)

            except:
                print("Arm_serial_servo_write serial error")
        else:
            pos = int((3100 - 900) * (angle - 0) / (180 - 0) + 900)
            value_H = (pos >> 8) & 0xFF
            value_L = pos & 0xFF
            time_H = (time >> 8) & 0xFF
            time_L = time & 0xFF

            try:
                cmd = [0xFF, 0xFC, 0x07, 0x10 + id, value_H, value_L, time_H, time_L]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)

            except:
                print("Arm_serial_servo_write serial er")

    # 버스 서보 각도 설정 인터페이스: s1~S4, s6: 0-180, S5: 0~270, time은 동작 시간
    def Arm_serial_servo_write6(self, s1, s2, s3, s4, s5, s6, time):
        # sleep(0.0015)
        if s1 > 180 or s2 > 180 or s3 > 180 or s4 > 180 or s5 > 270 or s6 > 180:
            print("参数传入范围不在0-180之内！")
            return
        try:
            pos = int((3100 - 900) * (s1 - 0) / (180 - 0) + 900)
            value1_H = (pos >> 8) & 0xFF
            value1_L = pos & 0xFF

            s2 = 180 - s2
            pos = int((3100 - 900) * (s2 - 0) / (180 - 0) + 900)
            value2_H = (pos >> 8) & 0xFF
            value2_L = pos & 0xFF

            s3 = 180 - s3
            pos = int((3100 - 900) * (s3 - 0) / (180 - 0) + 900)
            value3_H = (pos >> 8) & 0xFF
            value3_L = pos & 0xFF

            s4 = 180 - s4
            pos = int((3100 - 900) * (s4 - 0) / (180 - 0) + 900)
            value4_H = (pos >> 8) & 0xFF
            value4_L = pos & 0xFF

            pos = int((3700 - 380) * (s5 - 0) / (270 - 0) + 380)
            value5_H = (pos >> 8) & 0xFF
            value5_L = pos & 0xFF

            pos = int((3100 - 900) * (s6 - 0) / (180 - 0) + 900)
            value6_H = (pos >> 8) & 0xFF
            value6_L = pos & 0xFF

            time_H = (time >> 8) & 0xFF
            time_L = time & 0xFF
            s_id = 0x1D

            cmd = [
                0xFF,
                0xFC,
                0x11,
                0x1D,
                value1_H,
                value1_L,
                value2_H,
                value2_L,
                value3_H,
                value3_L,
                value4_H,
                value4_L,
                value5_H,
                value5_L,
                value6_H,
                value6_L,
                time_H,
                time_L,
            ]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)

        except:
            print("Arm_serial_servo_write6 serial error")

    # 임의 버스 서보 각도 설정 인터페이스: id: 1-250(0은 전체 제어) angle: 0-180 (900~3100, 0~180)
    def Arm_serial_servo_write_any(self, id, angle, time):
        if id != 0:
            pos = int((3100 - 900) * (angle - 0) / (180 - 0) + 900)
            value_H = (pos >> 8) & 0xFF
            value_L = pos & 0xFF
            time_H = (time >> 8) & 0xFF
            time_L = time & 0xFF
            try:
                cmd = [
                    0xFF,
                    0xFC,
                    0x08,
                    0x19,
                    id & 0xFF,
                    value_H,
                    value_L,
                    time_H,
                    time_L,
                ]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)

            except:
                print("Arm_serial_servo_write_any serial error")
        elif id == 0:  # 此为所有舵机控制 This is the control of all servos
            pos = int((3100 - 900) * (angle - 0) / (180 - 0) + 900)
            value_H = (pos >> 8) & 0xFF
            value_L = pos & 0xFF
            time_H = (time >> 8) & 0xFF
            time_L = time & 0xFF
            try:
                cmd = [
                    0xFF,
                    0xFC,
                    0x07,
                    0x17,
                    id & 0xFF,
                    value_H,
                    value_L,
                    time_H,
                    time_L,
                ]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)

            except:
                print("Arm_serial_servo_write_any serial error")

    # 원클릭 버스 서보 중간 위치 오프셋 설정, 전원 인가 후 중간 위치로 이동, 아래 함수 호출, id:1-6(설정), 0(초기화)
    def Arm_serial_servo_write_offset_switch(self, id):
        try:
            if id > 0 and id < 7:
                cmd = [0xFF, 0xFC, 0x04, 0x1C, id]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)

            elif id == 0:
                cmd = [0xFF, 0xFC, 0x04, 0x1C, 0x00]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)

        except:
            print("Arm_serial_servo_write_offset_switch serial error")

    # 원클릭 버스 서보 중간 위치 오프셋 상태 읽기, 0: 해당 서보 ID 없음, 1: 성공, 2: 실패(범위 초과)
    def Arm_serial_servo_write_offset_state(self):
        try:
            cmd = [0xFF, 0xFC, 0x03, 0x1B]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)

            self.__receive_data()
            sleep(0.002)
            sta = self.state
            return sta

        except:
            print("Arm_serial_servo_write_offset_state serial error")
        return Node

    # 버스 서보 각도 설정 인터페이스: 배열
    def Arm_serial_servo_write6_array(self, joints, time):
        s1, s2, s3, s4, s5, s6 = (
            joints[0],
            joints[1],
            joints[2],
            joints[3],
            joints[4],
            joints[5],
        )
        if s1 > 180 or s2 > 180 or s3 > 180 or s4 > 180 or s5 > 270 or s6 > 180:
            print(
                "参数传入范围不在0-180之内！The parameter input range is not within 0-180!"
            )
            return
        try:
            pos = int((3100 - 900) * (s1 - 0) / (180 - 0) + 900)
            value1_H = (pos >> 8) & 0xFF
            value1_L = pos & 0xFF

            s2 = 180 - s2
            pos = int((3100 - 900) * (s2 - 0) / (180 - 0) + 900)
            value2_H = (pos >> 8) & 0xFF
            value2_L = pos & 0xFF

            s3 = 180 - s3
            pos = int((3100 - 900) * (s3 - 0) / (180 - 0) + 900)
            value3_H = (pos >> 8) & 0xFF
            value3_L = pos & 0xFF

            s4 = 180 - s4
            pos = int((3100 - 900) * (s4 - 0) / (180 - 0) + 900)
            value4_H = (pos >> 8) & 0xFF
            value4_L = pos & 0xFF

            pos = int((3700 - 380) * (s5 - 0) / (270 - 0) + 380)
            value5_H = (pos >> 8) & 0xFF
            value5_L = pos & 0xFF

            pos = int((3100 - 900) * (s6 - 0) / (180 - 0) + 900)
            value6_H = (pos >> 8) & 0xFF
            value6_L = pos & 0xFF
            time_H = (time >> 8) & 0xFF
            time_L = time & 0xFF

            # cmd = [0xFF,0xFC,0x05,0x1e,time_H,time_L]
            # checksum = sum(cmd,5) & 0xff
            # cmd.append(checksum)
            # self.ser.write(cmd)

            cmd = [
                0xFF,
                0xFC,
                0x11,
                0x1E,
                value1_H,
                value1_L,
                value2_H,
                value2_L,
                value3_H,
                value3_L,
                value4_H,
                value4_L,
                value5_H,
                value5_L,
                value6_H,
                value6_L,
                time_H,
                time_L,
            ]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)

        except:
            print("Arm_serial_servo_write6 serial error")

    # RGB LED 지정 색상 설정
    def Arm_RGB_set(self, red, green, blue):
        try:
            cmd = [
                self.__HEAD,
                self.__DEVICE_ID,
                0x06,
                0x02,
                red & 0xFF,
                green & 0xFF,
                blue & 0xFF,
            ]
            checksum = sum(cmd, self.__COMPLEMENT) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)

        except:
            print("Arm_RGB_set serial error")

    # 부저 켜기, delay 기본값 0xff, 계속 울림
    def Arm_Buzzer_On(self, delay=0xFF):
        try:
            if delay != 0:
                cmd = [0xFF, 0xFC, 0x04, 0x06, delay & 0xFF]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)
        except:
            print("Arm_Buzzer_On serial error")

    # 부저 끄기
    def Arm_Buzzer_Off(self):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x06, 0x00]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
        except:
            print("Arm_Buzzer_On serial error")

    # 서보 각도 읽기, id:1-6
    def Arm_serial_servo_read(self, id):
        if id < 1 or id > 6:
            print("id must be 1 - 6")
            return None
        try:
            cmd = [0xFF, 0xFC, 0x03, id + 0x30]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)
            self.__receive_data()

            cmd = [0xFF, 0xFC, 0x03, id + 0x30]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)
            self.__receive_data()

            i = 0
            d = 0
            if self.id == (id + 0x30):
                pos = self.servo_H * 256
                dos = self.servo_L
                d = pos + dos
            else:
                self.__receive_data()
                i += 1
            if i > 3:
                i = 0
                return node

        except:
            print("Arm_serial_servo_read serial error")
            return None
        if d == 0:
            return None

        if id == 5:
            d = int((270 - 0) * (d - 380) / (3700 - 380) + 0)
            if d > 270 or d < 0:
                return None
        else:
            d = int((180 - 0) * (d - 900) / (3100 - 900) + 0)
            if d > 180 or d < 0:
                return None
        if id == 2 or id == 3 or id == 4:
            d = 180 - d
        return d

    # K1 버튼 모드 설정, 0: 기본 모드, 1: 학습 모드
    def Arm_Button_Mode(self, mode):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x03, mode & 0xFF]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
        except:
            print("Arm_Button_Mode serial error")

    # 학습 모드에서 현재 동작 1회 기록
    def Arm_Action_Study(self):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x24, 0x01]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
        except:
            print("Arm_Action_Study serial error")

    # 저장된 동작 그룹 개수 읽기
    def Arm_Read_Action_Num(self):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x22, 0x01]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)

            self.__receive_data()
            d = self.num
            return d

        except:
            print("Arm_Read_Action_Num serial error")

    # 동작 그룹 실행 모드 0: 정지, 1: 1회 실행, 2: 반복 실행
    def Arm_Action_Mode(self, mode):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x20, mode & 0xFF]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)

        except:
            print("Arm_Clear_Action serial error")

    # 동작 그룹 초기화
    def Arm_Clear_Action(self):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x23, 0x01]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.5)

        except:
            print("Arm_Clear_Action serial error")

    # 버전 정보
    def get_version():
        try:
            cmd = [0xFF, 0xFC, 0x03, 0x01]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            ser.write(cmd)

            self.__receive_data()
            sleep(0.002)
            d = self.version
            return d

        except:
            print("version error")
            return None

    # 버스 서보 각도 읽기, id: 1-250, 반환값 0-180
    def Arm_serial_servo_read_any(self, id):

        if id < 1 or id > 250:
            print("id must be 1 - 250")
            return none
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x37, id]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)

            self.__receive_data()
            sleep(0.002)
            pos = self.servo_H * 256
            dos = self.servo_L
            d = pos + dos

        except:
            print("version error")
            return None
        d = (d >> 8 & 0xFF) | (d << 8 & 0xFF00)
        d = int((180 - 0) * (d - 900) / (3100 - 900) + 0)

        return d

    # 서보 상태 읽기, 정상: 0xda, 데이터 없음: 0x00, 그 외: 서보 오류
    def Arm_ping_servo(self, id):
        data = int(id)
        if data > 0 and data <= 250:
            reg = 0x38
            cmd = [0xFF, 0xFC, 0x04, reg, data]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)

            value = 0  # rece
            times = 0
            while value == 0 and times < 5:
                cmd = [0xFF, 0xFC, 0x04, reg, data]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)
                sleep(0.001)

                value = 0
                times += 1
                if time >= 5:
                    return NODE
            return value
        else:
            return node

    # 토크 스위치 1: 토크 ON, 0: 토크 OFF(수동 조작 가능)
    def Arm_serial_set_torque(self, onoff):
        try:
            if onoff == 1:
                cmd = [0xFF, 0xFC, 0x04, 0x1A, 0x01]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)
                sleep(0.001)
            else:
                cmd = [0xFF, 0xFC, 0x04, 0x1A, 0x00]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)
                sleep(0.001)
        except:
            print("Arm_serial_set_torque serial error")

    # 버스 서보 ID 설정
    def Arm_serial_set_id(self, id):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x18, id & 0xFF]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)
        except:
            print("Arm_serial_set_id serial error")

    # 현재 제품 색상 설정 1~6, RGB LED 색상 지정
    def Arm_Product_Select(self, index):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x04, index & 0xFF]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)
        except:
            print("Arm_Product_Select serial erro")

    # 드라이버 보드 재시작
    def Arm_reset(self):
        try:
            cmd = [0xFF, 0xFC, 0x04, 0x05, 0x01]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)

        except:
            print("Arm_reset serial error")

    # PWM 서보 제어 id:1-6(0은 전체 제어) angle: 0-180
    def Arm_PWM_servo_write(self, id, angle):
        try:
            if id == 0:
                cmd = [0xFF, 0xFC, 0x04, 0x57, angle & 0xFF]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)
                sleep(0.001)
            else:
                cmd = [0xFF, 0xFC, 0x04, 0x50 + id, angle & 0xFF]
                checksum = sum(cmd, 5) & 0xFF
                cmd.append(checksum)
                self.ser.write(cmd)
                sleep(0.001)
        except:
            print("Arm_PWM_servo_write serial error")

    def Arm_voied_write(self):
        try:
            cmd = [0xFF, 0xFC, 0x03, 0x2A]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)
        except:
            print("Arm_PWM_servo_write serial error")

    def Arm_serial_speech_read(self, id):
        try:
            self.__receive_data()
            sleep(0.001)

            return self.speech_state
        except:
            return 0

    def Arm_ask_speech(self, id):
        try:
            cmd = [0xFF, 0xFC, 0x03, 0x60 + id]
            checksum = sum(cmd, 5) & 0xFF
            cmd.append(checksum)
            self.ser.write(cmd)
            sleep(0.001)
        except:
            print("iic error")
