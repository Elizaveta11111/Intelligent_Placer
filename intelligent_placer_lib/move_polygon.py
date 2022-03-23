from math import sqrt
import numpy as np
from cv2 import getAffineTransform


def vec(a, b):  # возвращает вектор от точки a до b
    return [b[0] - a[0], b[1] - a[1]]


def norm(v):  # норма вектора
    x = v[0]
    y = v[1]
    return sqrt(x * x + y * y)


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


def find_axes(p1, p2, p3):  # на заданной стороне определяет направление ортов
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
    return [[p1[0] + i[0], p1[1] + i[1]], p1, [p1[0] + j[0] * direction, p1[1] + j[1] * direction]]


def coord_transformation(poly, i):  # переносит многоугольник в начало координат
    dst_tri = np.array([[1, 0], [0, 0], [0, 1]]).astype(np.float32)
    src_tri = np.array([find_axes(poly[i - 1], poly[i], poly[(i + 1) % len(poly)])]).astype(np.float32)
    warp_mat = getAffineTransform(src_tri, dst_tri)
    new_poly = []
    for p in poly:
        new_poly.append(np.dot(warp_mat, np.append(p, 1)))
    return new_poly
