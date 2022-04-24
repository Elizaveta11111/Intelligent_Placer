from shapely.geometry import Polygon
from scipy.spatial import ConvexHull
from intelligent_placer_lib.utility import dist, norm, vec

areas = {'yellow_scissors': 150 * 40,
         'book': 150 * 110,
         'tool': 130 * 40,
         'mascara': 115 * 25,
         'scissors': 100 * 20,
         'stapler': 100 * 50,
         'tape': 70 * 70,
         'lighter': 80 * 25,
         'toy': 40 * 30,
         'heart': 25 * 25}


def find_closest(point, points_indexes, item):  # находит ближайшую точку предмета, лежащую на стороне
    d_min = 1000
    for i in points_indexes:
        p = item[i]
        d = dist(point, p)
        if d < d_min:
            d_min = d
            closest = i
    return closest


def cos(a, b):
    return (a[0] * b[0] + a[1] * b[1]) / (norm(a) * norm(b))


def get_direction(item, item_point_ind, polygon, poly_point_ind, k):
    c1 = cos(vec(item[item_point_ind], polygon[poly_point_ind]),
             vec(item[item_point_ind], item[(item_point_ind + 1) % k]))
    c2 = cos(vec(item[item_point_ind], polygon[poly_point_ind]),
             vec(item[item_point_ind], item[item_point_ind - 1]))
    # идем в том направлении, для которого угол меньше
    # этот способ не работает для выпуклых многоугольников
    if c1 > c2:
        return 1
    else:
        return -1


def start(i, polygon, points_assignment, visited, n):
    poly_point_ind = i
    new_polygon = [polygon[poly_point_ind]]
    while len(points_assignment[poly_point_ind]) == 0:
        visited.append(poly_point_ind)
        poly_point_ind = (poly_point_ind + 1) % n
        new_polygon.append(polygon[poly_point_ind])
    return new_polygon, poly_point_ind


def run_on_item(item, polygon, poly_point_ind, points_assignment, new_polygon, points_on_sides_list, k):
    item_point_ind = find_closest(polygon[poly_point_ind], points_assignment[poly_point_ind], item)
    new_polygon.append(item[item_point_ind])
    dir = get_direction(item, item_point_ind, polygon, poly_point_ind, k)
    item_point_ind = (item_point_ind + dir) % k
    new_polygon.append(item[item_point_ind])
    while item_point_ind not in points_on_sides_list:
        item_point_ind = (item_point_ind + dir) % k
        new_polygon.append(item[item_point_ind])
    return item_point_ind


def finish(item_point_ind, points_assignment, new_polygon, polygon, visited, first_point, n):
    for side in range(n):   # находим сторону многоугольника, на которой лежит точка
        if item_point_ind in points_assignment[side]:
            poly_point_ind = (side + 1) % n
            break
    while poly_point_ind != first_point:
        visited.append(poly_point_ind)
        new_polygon.append(polygon[poly_point_ind])
        poly_point_ind = (poly_point_ind + 1) % n


def update_polygon(polygon, item, points_on_sides_list, points_assignment, name):
    visited = []  # будем отмечать стороны, по которым уже прошли
    max_area = 0
    biggest_polygon = []
    n = len(polygon)
    k = len(item)
    poly_area = Polygon(polygon).area
    for i in range(n):
        if i in visited:
            continue
        visited.append(i)
        #  находим сторону на которой не лежат вершины предмета
        if len(points_assignment[i]) != 0:
            continue
        #  идем по многоугольнику, пока не встретим сторону на которой лежит вершина предмета 
        new_polygon, poly_point_ind = start(i, polygon, points_assignment, visited, n)
        #  дальше двигаемся вдоль предмета, выбрав сторону обхода так, чтобы угол между последней посещенной точкой 
        #  многоугольника и новой точкой предмета был минимален
        #  идем до тех пор, пока снова не встретим вершину, лежащую на многоугольнике
        item_point_ind = run_on_item(item, polygon, poly_point_ind, points_assignment, new_polygon,
                                     points_on_sides_list, k)
        # далее снова идем по многоугольнику, пока не вернемся к начальной точке
        finish(item_point_ind, points_assignment, new_polygon, polygon, visited, i, n)
        area = Polygon(new_polygon).area
        if area > max_area:
            if poly_area - area < areas[name] / 2:  # костыль на случай если новый многоугольник совпал со старым
                visited = []
                start(i, polygon, points_assignment, visited, n)
            else:  # из всех найденных многоугольников, выбираем тот у которого наибольшая площадь
                max_area = area  
                biggest_polygon = new_polygon
    deleted_area = poly_area - max_area
    if max_area == 0:
        return polygon, 297 * 210
    hull_poly_diff = ConvexHull(biggest_polygon).volume - max_area  # считаем разницу площади между полученным 
    # многоугольником и его выпуклой оболочкой
    return biggest_polygon, hull_poly_diff + deleted_area 
