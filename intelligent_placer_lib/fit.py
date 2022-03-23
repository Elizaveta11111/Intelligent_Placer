from intelligent_placer_lib.move_polygon import coord_transformation


items = {'book': ([[0, 0], [110, 0], [110, 150], [0, 150]],
                  [[0, 0], [150, 0], [150, 110], [0, 110]]),
         'lighter': ([[0, 0], [0, 80], [25, 80], [25, 0]],
                     [[0, 0], [0, 25], [80, 25], [80, 0]])}


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


def place_inside(item, poly):
    lines = get_sides_array(poly)  # координаты сторон многоугольника
    eps = 2
    points_inside = 0  # счетчик точек внутри многоугольника
    k = -1
    while k < len(item) - 1:  # цикл по всем точкам многоугольника
        k += 1
        p = item[k]
        j = p[1]
        i_min = None  # растояние до ближайшей стороны в направлении оси x
        intersection = 0  # число пересечений луча со сторонами многоугольника
        point_inside = False
        for line in lines:  # цикл по сторонам многоугольника
            A, B = get_A_B(line)  # А - нижняя точка прямой, B - верхняя
            if B[1] + eps > j > A[1] - eps:  # проверяем, что точка может пересечь сторону
                a = product([A, B], [A, p])  # вычисляем косое произведение
                if a > 100:  # если косое произведение положительно, то точка находится левее стороны
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
                    if a > -100:  # если косое произведение близко к нулю, то точка расположена на стороне
                        point_inside = True
                        continue
        if point_inside:  # точка на границе
            points_inside += 1
            continue
        if intersection % 2 == 1:  # точка внутри
            points_inside += 1
            continue
        if i_min is not None and intersection % 2 == 0:  # точка снаружи
            k = -1  # не помню почему но без этой строчки не работает
            points_inside = 0
            item = move_in_i(item, i_min)  # сдвигаем многоугольник
    return item, points_inside == len(item)  # возвращаем координаты предмета для визуализации



def fit_in_corner(poly, item, i):
    poly = coord_transformation(poly, i)
    item, inside = place_inside(item, poly)
    return inside, item, poly


def fit(poly, name):
    for item in items[name]:
        for i in range(len(poly)):
            inside, new_item, new_poly = fit_in_corner(poly, item, i)
            if inside:
                break
        if inside:
            break
    return inside, new_item, new_poly
