import numpy as np


def dist(p1, p2):
    x = p2[0] - p1[0]
    y = p2[1] - p1[1]
    return np.sqrt(x * x + y * y)


def apply_transformation(points, matrix):
    new_points = []
    for p in points:
        new_points.append(np.dot(matrix, np.append(p, 1)))
    return new_points


def vec(a, b):  # возвращает вектор от точки a до b
    return [b[0] - a[0], b[1] - a[1]]


def norm(v):  # норма вектора
    x = v[0]
    y = v[1]
    return np.sqrt(x * x + y * y)