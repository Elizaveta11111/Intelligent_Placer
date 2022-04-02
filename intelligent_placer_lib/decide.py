import numpy as np
from intelligent_placer_lib.utility import dist


def isStapler(r, g, b, mask, pixels_number):
    pink_area = 0
    for i in range(len(mask)):
        for j in range(len(mask[0])):
            pink_area += g[i][j] < r[i][j] < b[i][j]
    if pink_area * 4 > pixels_number:
        return True
    else:
        return False


def isScissors(item_box, pixels_number, w):
    box_area = dist(item_box[0], item_box[1]) * dist(item_box[1], item_box[2])
    if pixels_number * 2 < box_area and w > 15:
        return True
    else:
        return False


def isBlue(r, g, b, mask, pixels_number):
    blue_area = 0
    for i in range(len(mask)):
        for j in range(len(mask[0])):
            blue_area += r[i][j] > b[i][j] and r[i][j] > g[i][j]
    if blue_area * 5 > pixels_number:
        return True
    else:
        return False


def isRed(r, g, b, mask, pixels_number):
    red_area = 0
    for i in range(len(mask)):
        for j in range(len(mask[0])):
            red_area += b[i][j] > r[i][j] and b[i][j] > g[i][j] and b[i][j] - r[i][j] > (g[i][j] - r[i][j]) * 2
    if red_area * 1.5 > pixels_number:
        return True
    else:
        return False


# определяет предмет на изображении
def decide(item_box, transformation_matrix, mask, img):
    # находим число пикселей в маске
    pixels_number = np.sum(mask)
    # выделим rgb компоненты изображения, чтобы рапозновать предметы по цвету
    r = img[..., 0] * mask
    g = img[..., 1] * mask
    b = img[..., 2] * mask

    # сначала определим является ли предмет степлером, посчитав количество розовых пикселей
    if isStapler(r, g, b, mask, pixels_number):
        return 'stapler'

    # масштабируем ограничивающий четырехугольник, чтобы оценить размеры предметов
    item_box_transformed = []
    for p in item_box:
        item_box_transformed.append(np.dot(transformation_matrix, np.append(p, 1)))
    # находим длинну и ширину
    side1 = dist(item_box_transformed[0], item_box_transformed[1])
    side2 = dist(item_box_transformed[1], item_box_transformed[2])
    h = max(side1, side2)
    w = min(side1, side2)

    # проверяем является ли предмет ножницами по отношению площади маски к площади ограничивающего четырехугольника
    if isScissors(item_box, pixels_number, w):
        if w > 60:
            return 'yellow_scissors'
        else:
            return 'scissors'

    # оставшиеся предметы определяем по размерам и цвету
    if 90 < h < 150 and 25 < w < 45:
        if isBlue(r, g, b, mask, pixels_number):
            return 'tool'
        else:
            return 'mascara'
    if 140 < h < 160 and 90 < w < 120:
        return 'book'
    if 70 < h < 90 and 15 < w < 35:
        return 'lighter'
    if 15 < h < 30 and 15 < w < 30:
        if isRed(r, g, b, mask, pixels_number):
            return 'heart'
        else:
            return None
    if 30 < h < 60 and 15 < w < 40:
        return 'toy'
    if 60 < h < 100 and 60 < w < 90:
        return 'tape'
    else:
        return None
