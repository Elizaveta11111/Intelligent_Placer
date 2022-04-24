import numpy as np
from cv2 import getAffineTransform
from skimage.measure import points_in_poly
from intelligent_placer_lib.utility import norm, vec


def side_len(a):  # длинна стороны
    return norm(vec(a[0], a[1]))


def normalize(v):  # нормализует вектор
    vector_len = norm(v)
    return [v[0] / vector_len, v[1] / vector_len]


def cos_sign(a, b):  # возвращает знак косинуса между векторами
    if a[0] * b[0] + a[1] * b[1] > 0:
        return 1
    else:
        return -1


def check_if_convex(poly, i):  # проверяет является ли угол выпуклым или нет
    p1 = poly[i - 1]
    p2 = poly[(i + 1) % len(poly)]
    middle = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)  # определяем середину отрезка, соединяющего концы угла
    return points_in_poly([middle], poly)  # если она лежит внутри многоугольника - угол выпуклый


def find_axes(poly, k):  # на заданной стороне определяет направление ортов
    p3 = poly[k - 1]
    p2 = poly[k]
    p1 = poly[(k + 1) % len(poly)]
    i = normalize(vec(p1, p2))  # выбираем одну из сторон как направление оси x
    ax = i[0]
    ay = i[1]
    if ax != 0:
        bx = -ay / ax
        by = 1
    else:
        bx = 1
        by = -ax / ay
    j = normalize([bx, by])  # находим перепендикулярный ей вектор
    direction = cos_sign(j, vec(p1, p3))  # ось y должна составлять угол меньше прямого со второй стороной
    if not check_if_convex(poly, k):  # и больше прямого для невыпуклого многоугольника
        direction = -direction
    return [[p1[0] + i[0], p1[1] + i[1]], p1, [p1[0] + j[0] * direction, p1[1] + j[1] * direction]]


def coord_transformation(poly, i):  # возвращает отображение, переносящее многоугольник в начало координат
    dst_tri = np.array([[1, 0], [0, 0], [0, 1]]).astype(np.float32)
    src_tri = np.array([find_axes(poly, i)]).astype(np.float32)
    return getAffineTransform(src_tri, dst_tri)
