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
    q = queue.Queue()
    rs = RobokitRS.RobokitRS()
    port = get_serial_port()
    if port is None:
        print("시리얼 포트를 찾을 수 없습니다.")
        return
    rs.port_open(port)
    rs.sonar_begin(13)
    rs.set_pin_mode(12, RobokitRS.Modes.INPUT)
    rs.set_pin_mode(2, RobokitRS.Modes.INPUT)

    is_getting = False
    frame = np.zeros((240, 320, 3), np.uint8)
    thr = None
    global running
    running = True
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    start_time = time.time()
    state = "tracking"  # 상태: tracking → parking → tracking2

    while running:
        new_frame = None
        distance = rs.sonar_read(13)
        ir_f, ir_b = rs.digital_reads([12, 2])

        if not is_getting:
            thr = Thread(target=get_robo_image, args=(q,))
            thr.start()
            is_getting = True

        thr.join(0.5)
        x = 1
        if thr.is_alive():
            print("can not get img")
            x = 0
        else:
            is_getting = False
            new_frame = q.get()
        if not is_getting:
            frame = new_frame

        cv2.imshow("frame", frame)

        current_time = time.time()
        elapsed = current_time - start_time

        if state == "tracking":
            action(rs, frame, (distance, ir_f, ir_b), prams, x)
            if elapsed > 17:
                state = "parking"
                stop(rs)
                parking(rs)
                start_time = time.time()  # 타이머 초기화q
        elif state == "parking":
            state = "tracking2"
        elif state == "tracking2":
            action(rs, frame, (distance, ir_f, ir_b), prams, x)

        cv2.waitKey(1)

    rs.end()
    listener.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    move_robo(line_tracking, 1, 2, 3)  # 움직이는 함수 실행
