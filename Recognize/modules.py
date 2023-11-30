# modules.py
import cv2
import numpy as np
import functions as fs
import os

def remove_noise(image):
    image = fs.threshold(image)  # 이미지 이진화
    mask = np.zeros(image.shape, np.uint8)  # 보표 영역만 추출하기 위해 마스크 생성
    subimages = []  # subimage들을 저장할 리스트
    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(image)  # 레이블링
    for i in range(1, cnt):
        x, y, w, h, area = stats[i]
        if w > image.shape[1] * 0.5:  # 보표 영역에만
            cv2.rectangle(mask, (x, y, w, h), (255, 0, 0), -1)  # 사각형 그리기

            # 원본 이미지에서 사각형 영역 추출하여 subimages 리스트에 추가
            subimage =[x, y, w, h]
            subimages.append(subimage)

    masked_image = cv2.bitwise_and(image, mask)  # 보표 영역 추출

    return masked_image, subimages


def split_and_save_staves(images, output_folder="split_staves_images"):
    split_images = []  # 분리된 이미지들을 저장할 리스트

    for idx, image in enumerate(images):
        height, width = image.shape
        staves = []  # 오선의 좌표들이 저장될 리스트

        # 이미지에서 오선 찾기
        for row in range(height):
            pixels = np.sum(image[row, :] == 255)
            if pixels >= width * 0.5:
                if len(staves) == 0 or abs(staves[-1][0] + staves[-1][1] - row) > 1:
                    staves.append([row, 0])
                else:
                    staves[-1][1] += 1

        # 오선이 5개 미만인 경우, 원본 이미지 저장
        if len(staves) < 5:
            print(f"이미지 {idx + 1}에서 5개 이상의 오선을 찾지 못했습니다. 원본 이미지를 저장합니다.")
            split_images.append(image)
            continue

        # 5번째 오선의 끝 위치 계산
        fifth_staff_end = int((staves[4][0] + staves[5][0]) / 2)

        # 오선 5번째까지 포함하는 부분
        top_part = image[:fifth_staff_end, :]

        # 나머지 부분
        bottom_part = image[fifth_staff_end:, :]

        # 리스트에 추가 (top part와 bottom part 순서대로)
        split_images.append(top_part)
        split_images.append(bottom_part)

    # 폴더 생성 및 이미지 저장
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for idx, split_image in enumerate(split_images):
        image_path = os.path.join(output_folder, f"part_{idx + 1}.png")
        cv2.imwrite(image_path, split_image)
        print(f"분리된 이미지 {idx + 1} 저장: {image_path}")

    print("모든 이미지 처리 완료.")

    return split_images

def remove_staves(image):
    height, width = image.shape
    staves = []  # 오선의 좌표들이 저장될 리스트

    for row in range(height):
        pixels = 0
        for col in range(width):
            pixels += (image[row][col] == 255)  # 한 행에 존재하는 흰색 픽셀의 개수를 셈
        if pixels >= width * 0.5:  # 이미지 넓이의 50% 이상이라면
            if len(staves) == 0 or abs(staves[-1][0] + staves[-1][1] - row) > 1:  # 첫 오선이거나 이전에 검출된 오선과 다른 오선
                staves.append([row, 0])  # 오선 추가 [오선의 y 좌표][오선 높이]
            else:  # 이전에 검출된 오선과 같은 오선
                staves[-1][1] += 1  # 높이 업데이트

    for staff in range(len(staves)):
        top_pixel = staves[staff][0]  # 오선의 최상단 y 좌표
        bot_pixel = staves[staff][0] + staves[staff][1]  # 오선의 최하단 y 좌표 (오선의 최상단 y 좌표 + 오선 높이)
        for col in range(width):
            if image[top_pixel - 1][col] == 0 and image[bot_pixel + 1][col] == 0:  # 오선 위, 아래로 픽셀이 있는지 탐색
                for row in range(top_pixel, bot_pixel + 1):
                    image[row][col] = 0  # 오선을 지움

    return image, [x[0] for x in staves]

def normalization(image, staves, standard):
    avg_distance = 0
    lines = int(len(staves) / 5)  # 보표의 개수
    for line in range(lines):
        for staff in range(4):
            staff_above = staves[line * 5 + staff]
            staff_below = staves[line * 5 + staff + 1]
            avg_distance += abs(staff_above - staff_below)  # 오선의 간격을 누적해서 더해줌
    avg_distance /= len(staves) - lines  # 오선 간의 평균 간격

    height, width = image.shape  # 이미지의 높이와 넓이
    weight = standard / avg_distance  # 기준으로 정한 오선 간격을 이용해 가중치를 구함
    new_width = int(width * weight)  # 이미지의 넓이에 가중치를 곱해줌
    new_height = int(height * weight)  # 이미지의 높이에 가중치를 곱해줌

    image = cv2.resize(image, (new_width, new_height))  # 이미지 리사이징
    # ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이미지 이진화 !! 이진화 작업시 음표 손실됨
    staves = [x * weight for x in staves]  # 오선 좌표에도 가중치를 곱해줌

    return image, staves