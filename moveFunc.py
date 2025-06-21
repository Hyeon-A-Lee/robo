from RobokitRS import *
import numpy as np
import time

# 모터 회전 방향은 f_list 에서 조절
speedSet = 3
maxSpeed = 15


# 직진 함수.
def forward(rs: RobokitRS.RobokitRS, speed: int = speedSet):
    f_list = np.array([1, 0, 1, 0])  # 0일 경우는 시계방향, 1일 경우 반시계 방향
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)


def right(rs: RobokitRS.RobokitRS, speed: int = speedSet):
    f_list = np.array([1, 0, 1, 1])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        if i == 0:
            rs.motor_write(i, f_list[i], maxSpeed)
            continue
        rs.motor_write(i, f_list[i], speed)


def hardright(rs: RobokitRS.RobokitRS, speed: int = speedSet):
    f_list = np.array([1, 1, 1, 1])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)


def left(rs: RobokitRS.RobokitRS, speed: int = speedSet):
    f_list = np.array([1, 0, 0, 0])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        if i == 1:
            rs.motor_write(i, f_list[i], maxSpeed)
            continue
        rs.motor_write(i, f_list[i], speed)


def hardLeft(rs: RobokitRS.RobokitRS, speed: int = speedSet):
    f_list = np.array([0, 0, 0, 0])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)


def stop(rs: RobokitRS.RobokitRS, speed: int = 0):
    f_list = np.array([1, 0, 0, 0])
    if speed < 0:
        f_list = -f_list + 1
        speed *= -1
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)


def parking(rs: RobokitRS.RobokitRS, speed: int = speedSet):
    print("주차 시작")

    # 1. 오른쪽 평행주차 동작: 모터 4개에 대해 [1, 1, 0, 0] 신호 출력
    f_list = np.array([1, 1, 0, 0])
    if speed < 0:
        f_list = -f_list + 1  # 속도가 음수일 때 신호 반전
        speed *= -1

    # 주차 동작 2초간 수행
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)
    time.sleep(5)

    # 2. 3초간 휴식 (모터 정지)
    for i in range(4):
        rs.motor_write(i, 0, 0)
    time.sleep(3)

    # 3. 왼쪽으로 탈출 동작: [0, 0, 1, 1] 신호 출력
    print("주차 탈출")
    f_list = np.array([0, 0, 1, 1])
    for i in range(4):
        rs.motor_write(i, f_list[i], speed)
    time.sleep(5)  # 2초간 탈출

    # 탈출 후 정지
    for i in range(4):
        rs.motor_write(i, 0, 0)

    print("주차 완료")
