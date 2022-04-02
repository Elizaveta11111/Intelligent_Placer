from intelligent_placer_lib.move_polygon import coord_transformation
from intelligent_placer_lib.utility import apply_transformation, dist

items = {'yellow_scissors': ([[0, 0], [35, 0], [70,25], [105, 0], [140, 0], [140, 40], [90, 50], [135, 120], [70, 65],
                              [5, 120], [50, 50], [0, 40]],
                             [[0, 0], [45, 0], [50, 45], [110, 0], [65, 65], [125, 125], [50, 90], [45, 135], [5, 135],
                              [5, 110], [30, 65], [0, 35]]),
         'book': ([[0, 0], [110, 0], [110, 150], [0, 150]],
                  [[0, 0], [150, 0], [150, 110], [0, 110]]),
         'tool': ([[0, 0], [0, 130], [40, 130], [40, 0]],
                  [[0, 0], [0, 40], [130, 40], [130, 0]]),
         'mascara': ([[0, 0], [0, 115], [25, 115], [25, 0]],
                     [[0, 0], [0, 25], [115, 25], [115, 0]]),
         'scissors': ([[0, 0], [105, 0], [45, 25], [30, 45], [10, 50], [0, 20]],
                      [[0, 0], [105, 0], [105, 20], [95, 50], [75, 45], [60, 25]],
                      [[0, 0], [50, 0], [50, 20], [35, 30], [25, 105], [15, 30], [0, 20]],
                      [[0, 105], [50, 105], [50, 85], [35, 75], [25, 0], [15, 75], [0, 85]]),
         'stapler': ([[0, 0], [0, 100], [50, 100], [50, 0]],
                      [[0, 0], [0, 50], [100, 50], [80, 0]]),
         'tape': ([[0, 0], [0, 70], [70, 70], [70, 0]], []),
         'lighter': ([[0, 0], [0, 80], [25, 80], [25, 0]],
                     [[0, 0], [0, 25], [80, 25], [80, 0]]),
         'toy': ([[0, 0], [0, 40], [30, 40], [30, 0]],
                 [[0, 0], [0, 30], [40, 30], [40, 0]]),
         'heart': ([[0, 0], [0, 25], [25, 25], [25, 0]], [])}


def get_sides_array(polygon):
    lines = []
    for i in range(len(polygon) - 1):
        lines.append([polygon[i], polygon[i + 1]])
    lines.append([polygon[len(polygon) - 1], polygon[0]])
    return lines


def product(a, b):
    x1 = a[1][0] - a[0][0]
    y1 = a[1][1] - a[0][1]
    x2 = b[1][0] - b[0][0]
    y2 = b[1][1] - b[0][1]
    return x1 * y2 - x2 * y1


def move_in_i(item, i):
    new_item = []
    for p in item:
        new_item.append([p[0] + i, p[1]])
    return new_item


def get_A_B(line):
    if line[0][1] < line[1][1]:
        A = line[0]
        B = line[1]
    else:
        A = line[1]
        B = line[0]
    return A, B


def intersection_count(item, k, lines, eps, points_on_sides_list, points_assignment):
    p = item[k]
    j = p[1]
    i_min = None  # растояние до ближайшей стороны в направлении оси x
    intersection = 0  # число пересечений луча со сторонами многоугольника
    point_on_border = False
    for s in range(len(lines)):  # цикл по сторонам многоугольника
        line = lines[s]
        A, B = get_A_B(line)  # А - нижняя точка прямой, B - верхняя
        if B[1] + eps > j > A[1] - eps:  # проверяем, что точка может пересечь сторону
            a = product([A, B], [A, p])  # вычисляем косое произведение
            if a > 300:  # если косое произведение положительно, то точка находится левее стороны
                x = B[0] - A[0]
                y = B[1] - A[1]
                if y > eps:
                    i = (j - A[1]) * x / y
                else:  # случай когда сторона почти горизонтальна
                    i = 0
                i = i + A[0] - p[0]
                i = abs(i)
                intersection += 1
                if i_min is None or i < i_min:
                    i_min = i
            else:
                if a > -500:  # если косое произведение близко к нулю, то точка расположена на стороне
                    d1 = dist(p, line[0])
                    d2 = dist(p, line[1])
                    d = dist(line[0], line[1])
                    if d1 <= d and d2 <= d:  # проверяем, что точка лежит на отрезке
                        if a > -300:
                            point_on_border = True
                        if p not in points_on_sides_list:
                            points_on_sides_list.append(k)
                            points_assignment[s].append(k)
                        continue
    return point_on_border, intersection, i_min


def place_inside(item, poly):
    points_on_sides_list = []
    points_assignment = [None] * len(poly)
    for i in range(len(points_assignment)):
        points_assignment[i] = []
    lines = get_sides_array(poly)  # координаты сторон многоугольника
    eps = 1
    points_inside = 0  # счетчик точек внутри многоугольника
    k = -1
    while k < len(item) - 1:  # цикл по всем точкам многоугольника
        k += 1
        point_on_border, intersection, i_min = intersection_count(item, k, lines, eps, points_on_sides_list,
                                                                  points_assignment)
        if point_on_border:  # точка на границе
            points_inside += 1
            continue
        if intersection % 2 == 1:  # точка внутри
            points_inside += 1
            continue
        if i_min is not None and intersection % 2 == 0:  # точка снаружи
            k = -1  # возможно, что после сдвига точки которые были внутри окажутся снаружи, поэтому начинаем заново
            points_inside = 0
            item = move_in_i(item, i_min)  # сдвигаем многоугольник
    return item, points_inside == len(
        item), points_on_sides_list, points_assignment  # возвращаем координаты предмета для визуализации


def fit_in_corner(poly, item, i):
    matrix = coord_transformation(poly, i)
    poly = apply_transformation(poly, matrix)
    item, inside, points_on_sides_list, points_assignment = place_inside(item, poly)
    return inside, item, poly, points_on_sides_list, points_assignment, matrix


def fit(poly, name):
    poly_arr = []
    item_arr = []
    points_on_sides_list_arr = []
    points_assignment_arr = []
    matrix_arr = []
    for item in items[name]:  # для каждого предмета находим все размещения, при которых он лежит внутри многоугольника
        if len(item) == 0:
            break
        for i in range(len(poly)):
            # информация о размещении - положение предмета и многоугольника; список вершин предмета, 
            # лежащих на сторонах; список вершин, лежащих на каждой из сторон; матрица, описывающая изменение положения 
            # многоугольника
            inside, new_item, new_poly, points_on_sides_list, points_assignment, matrix = fit_in_corner(poly, item, i)
            if inside:
                poly_arr.append(new_poly)
                item_arr.append(new_item)
                points_on_sides_list_arr.append(points_on_sides_list)
                points_assignment_arr.append(points_assignment)
                matrix_arr.append(matrix)
    return item_arr, poly_arr, points_on_sides_list_arr, points_assignment_arr, matrix_arr
