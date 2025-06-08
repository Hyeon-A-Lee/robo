from RobokitRS import *
import keyboard
from threading import Thread
import queue
from testcam import *
from maskmean import *
import cv2
import serial.tools.list_ports
from pynput import keyboard

speedSetting = 3


def get_serial_port():  # 윈도우 전용
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "COM" in port.device:
            return port.device

# def get_serial_port():
#     ports = list(serial.tools.list_ports.comports())
#     for port in ports:
#         if "usbserial" in port.device or "tty.usbmodem" in port.device:
#             return port.device
#     return None


def on_press(key):
    global running
    try:
        if key.char == 'q':
            running = False
    except AttributeError:
        if key == keyboard.Key.esc:
            running = False


def move_robo(action, *prams):
    q = queue.Queue()  # 큐 생성 / 카메라 이미지 데이터를 저장하기 위 큐 객체를 생성합니다.

    rs = RobokitRS.RobokitRS()  # 로봇 객체 생성

    # macOS 포트 번호 자동 탐지
    port = get_serial_port()  # 시리얼 포트 자동 탐지
    if port is None:
        print("시리얼 포트를 찾을 수 없습니다.")
        return

    rs.port_open(port)  # 시리얼 포트 열기 / 로봇통신

    rs.sonar_begin(13)  # 초음파 센서 입력 버퍼 열기

    # 버퍼를 열지 않으면 실행 X
    # 적외선 센서 입력 버퍼 열기 12: F, 2: B
    rs.set_pin_mode(12, RobokitRS.Modes.INPUT)
    rs.set_pin_mode(2, RobokitRS.Modes.INPUT)

    is_getting = False  # 카메라 이미지 수신 상태 플래그 / 처음에는 이미지를 수신하지 않기 때문에 False
    frame = np.zeros((240, 320, 3), np.uint8)  # 초기 프레임 설정
    # 카메라의 크기만큼 검정 빈 이미지를 생성한다.
    thr = None  # 스레드 초기화 / 병렬 실행을 위해 사용한다
    # 사용하는 이유는 사용자 인터페이스를 멈추지 않고 백그라운드 작업을 수행하고 싶어 사용한다.
    # 카메라 인식을 받으면서 이동

    global running
    running = True  # 프로그램 실행 상태 플래그

    listener = keyboard.Listener(on_press=on_press)  # 키보드 리스너 설정
    # 키보드로 특정 키를 눌렀을 때 종료하기 위해 키보드 리스너를 사용한다.
    listener.start()  # 키보드 리스너 시작
    while running:
        new_frame = None

        distance = rs.sonar_read(13)  # 초음파 센서로 거리 측정
        ir_f, ir_b = rs.digital_reads([12, 2])  # 적외선 센서로 데이터 읽기

        if not is_getting:
            thr = Thread(target=get_robo_image, args=(q,))  # 카메라 이미지 수신 스레드 시작
            thr.start()
            is_getting = True
        # 카메라 이미지가 수신하지 않는다면 image를 가져오는 함수를 실행한다. 이미지를 가져와 q에 저장하는 코드
        # 이미지를 가져온 후 스레드를 시작하고, is_getting을 True로 설정하여
        # 이미지를 가져왔다는 의미를 나타낸다.

        thr.join(0.5)  # 스레드가 종료될 때까지 최대 0.5초 대기
        x = 1
        if thr.is_alive():
            print("can not get img")
            x = 0
        else:
            is_getting = False  # 새로운 이미지를 가져오기 위해 스레드를 종료 시키기 위한 False
            new_frame = q.get()  # 새로운 프레임 가져오기

        if not is_getting:  # 스레드가 종료 됐을 때 새로운 이미지를 가져오기 위한 if 문
            frame = new_frame  # 새로운 이미지를 가져온다.

        cv2.imshow("frame", frame)  # 프레임(이미지) 출력

        action(rs, frame, (distance, ir_f, ir_b), prams, x)  # 동작 함수 호출

        cv2.waitKey(1)  # 키 입력 대기

    rs.end()  # 로봇 종료
    listener.stop()  # 키보드 리스너 종료
    cv2.destroyAllWindows()  # 모든 OpenCV 창 닫기


if __name__ == '__main__':
    move_robo(line_tracking, 1, 2, 3)  # 움직이는 함수 실행
