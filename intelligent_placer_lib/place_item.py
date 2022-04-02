from intelligent_placer_lib.fit import fit
from intelligent_placer_lib.update_polygon import update_polygon


def place_item(poly, name):
    min_area = 297 * 210
    item_arr, poly_arr, points_on_sides_list_arr, points_assignment_arr, matrix_arr = fit(poly, name)
    for i in range(len(item_arr)):  # для каждого варианта размещения
        item = item_arr[i]
        poly = poly_arr[i]
        points_on_sides_list = points_on_sides_list_arr[i]
        points_assignment = points_assignment_arr[i]
        matrix = matrix_arr[i]
        poly, area = update_polygon(poly, item, points_on_sides_list, points_assignment, name)  # находим новый многоугольник
        if area < min_area:  # и выбираем оптимальный
            min_area = area
            biggest_polygon = poly
            item_fit = item
            transformation = matrix
    if len(item_arr) == 0 or min_area == 297 * 210:
        return None, None, None
    return biggest_polygon, item_fit, transformation


def place_items(polygon, items_names):
    for i in range(len(items_names)):  # размещаем объекты в многоугольике в устанвленном порядке
        name = items_names[i]
        polygon, item, matrix = place_item(polygon, name)
        if polygon is None:
            return False
    return True
