import cv2
import numpy as np
from sympy import print_glsl

from moveFunc import *
# 마지막으로 저장된 num_mean 값을 저장하는 전역 변수
last_num_mean = None


def maskmean(img):
    global last_num_mean

    # BGR 이미지를 HSV 이미지로 변환
    # HSV 색상 공간은 색상(Hue), 채도(Saturation), 명도(Value)로
    # 구성되어 있어 색상 범위를 지정하기에 BGR보다 더 적합합니다.
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSV 범위 지정 (주어진 클릭된 범위에 기초)
    lower_hue = 16
    upper_hue = 35
    lower_saturation = 50
    upper_saturation = 90
    lower_value = 129
    upper_value = 255

    # 노란선으로 인식하기 위해 마스크를 생성하는데 생성하기 전에 범위를 지정한다.
    lower_hsv = np.array([lower_hue, lower_saturation, lower_value])
    upper_hsv = np.array([upper_hue, upper_saturation, upper_value])

    # 노란색 범위에 해당하는 마스크 생성
    mask = cv2.inRange(hsv_img, lower_hsv, upper_hsv)

    # 생성된 이미지에서 255인 부분을 찾아서 저장한다.
    num = np.where(mask == 255)


     # x좌표의 평균 값을 저장한다. 저장한 값을 이용해 좌우를 설정할 수 있다.
    if num[0].size == 0:  # 비어있는 경우
        num_mean = 160  # 중앙으로 대체
    else:  # x좌표의 평균 값을 저장한다. 저장한 값을 이용해 좌우를 설정할 수 있다.
        num_mean = int(np.mean(num[1]))

    # 마스크에서 0이 아닌 픽셀의 개수를 구함
    # 일정 이상 노란선을 찾지 못하게 되면 마지막에 이동하던 방향을 저장한다.
    # 직각 코스에서 선을 벗어나게 되는 경우를 대비
    non_zero_count = np.count_nonzero(mask)
    if non_zero_count < 500:
        if last_num_mean is not None:
            if last_num_mean < 160:
                return 20
            else:
                return 300
            return last_num_mean
        else:
            return 0

    # 노란 선이 충분히 감지 되었을 경우 실행

    # 현재 num_mean 값을 마지막 값으로 저장
    last_num_mean = num_mean

    cv2.circle(img, (num_mean, 120), 5, (0, 0, 255), -1)
    # 결과 이미지와 마스크 이미지를 디스플레이
    cv2.imshow('Original Image', img)
    cv2.imshow('Mask', mask)

    return num_mean



def line_tracking(rs, frame, sensor, prams, x):
    speedSetting = 4
    tspeed = 3
    if x == 0:  # 카메라가 멈춰서 이미지를 불러오지 못할 경우 자동차를 멈춘다.
        stop(rs, 0)
    else:
        mx = maskmean(frame)  # 마스크 함수를 이용해서 이미지의 노란선을 찾는다
        # 노란선 부분의 평균 값을 구해 mx로 반환해준다. x 좌표를 반환한다.
        # 반환된 x 좌표를 이용해 좌, 우를 구분한다.



        padding = 40  # 패딩값을 줘 영역을 나눈다.


        if mx > 160 + padding + 90:  # 심하게 오른쪽일 경우 자리에서 방향 전환
            print("hardright 실행")
            hardright(rs, tspeed)
            # print(">> parking 실행 중...")
            # parking(rs)
            # print(">> parking 종료, 다시 라인 따라감")
        elif mx > 160 + padding:  # 원을 그리며 오른쪽으로 회전
            print("right 실행")
            right(rs, tspeed)
        elif mx > 160 - padding:  # 직진
            print("forward 실행")
            forward(rs, speedSetting)
        elif mx > 160 - padding - 90:  # 원을 그리며 왼쪽으로 회전
            print("left 실행")
            left(rs, tspeed)
        else:
            print("hardleft 실행")
            hardLeft(rs, speedSetting)  # 자리에서 왼쪽으로 방향 전환
        # right(rs, speedSetting)

# 테스트용 코드
if __name__ == "__main__":
    # 예제 이미지 로드 (경로를 실제 이미지 파일 경로로 변경하세요)
    img = cv2.imread("example.jpg")
    maskmean(img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # if num[0].size == 0:  # 비어있는 경우------------------
    #     num_mean = 160  # 중앙으로 대체--------------------

