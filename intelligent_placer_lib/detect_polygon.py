from skimage.filters import threshold_triangle
import numpy as np
import cv2
from skimage.morphology import binary_closing
from skimage.measure import regionprops
from skimage.measure import label as sk_measure_label


def binary(img):
    thresh_tri = threshold_triangle(img)
    res = img > thresh_tri
    return res


def get_components(mask):
    labels = sk_measure_label(mask)  # разбиение маски на компоненты связности
    props = regionprops(labels)  # нахождение свойств каждой области
    areas = [prop.area for prop in props]  # нас интересуют площади компонент связности
    boxes = [prop.bbox for prop in props]
    # находим две наибольшие компоненты связности - это лист и многоугольник
    first = np.array(areas).argmax()
    areas[first] = 0
    second = np.array(areas).argmax()
    # при этом многоугольник не может лежать за пределами листа
    if boxes[first][0] < boxes[second][0]:
        return labels == (first + 1), labels == (second + 1)
    else:
        return labels == (second + 1), labels == (first + 1)


def paper_edges(paper):
    contours, hierarchy = cv2.findContours(paper, 1, 2)  # поиск контуров на ихображении
    cnt = contours[0]  # на изображении только один предмет - лист
    rect = cv2.minAreaRect(cnt)  # поиск наименьшего по площади многоугольника, ограничивающего лист
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    return box


def poly_edges(poly):
    contours, hierarchy = cv2.findContours(poly, 1, 2)  # поиск контуров на изображении
    cnt = contours[0]  # на изображении только один предмет - многоугольник
    perimeter = cv2.arcLength(cnt, True)
    shape = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)  # переходим от контура к многоугольнику
    return shape[:, 0]


def product(a, b):
    x1 = a[1][0] - a[0][0]
    y1 = a[1][1] - a[0][1]
    x2 = b[1][0] - b[0][0]
    y2 = b[1][1] - b[0][1]
    return x1 * y2 - x2 * y1


def dist(p1, p2):
    x = p2[0] - p1[0]
    y = p2[1] - p1[1]
    return x * x + y * y


# распологаем стороны так, чтобы сначала шла длиная сторона, а затем короткая
# далее необходимо выбрать угол, для которого векторное произведение сторон было бы направлено потив оси z.
def find_corner(paper):
    if dist(paper[0], paper[1]) > dist(paper[1], paper[2]):
        tri = [paper[0], paper[1], paper[2]]
    else:
        tri = [paper[2], paper[1], paper[1]]
    if product([tri[1], tri[0]], [tri[1], tri[2]]) > 0:
        return tri
    if dist(paper[1], paper[2]) > dist(paper[3], paper[2]):
        tri = [paper[1], paper[2], paper[3]]
    else:
        tri = [paper[3], paper[2], paper[1]]
    return tri


def coord_transformation(poly, paper):
    srcTri = np.array(find_corner(paper)).astype(np.float32)  # находим левый нижний угол листа на изображении
    dstTri = np.array([[0, 297], [0, 0], [210, 0]]).astype(np.float32)  # три точки которые мы хотим ему сопоставить
    warp_mat = cv2.getAffineTransform(srcTri, dstTri)  # находим нужное отображение
    new_poly = []
    for p in poly:
        new_poly.append(np.dot(warp_mat, np.append(p, 1)))  # применяем его к многоугольнику
    return np.array(new_poly), warp_mat


def detect_polygon(path_to_image):
    img = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)

    mask = binary(img)  # бинаризуем изображение
    paper, poly = get_components(mask)  # находим две самые большие компоненты связности - это лист и многоугольник
    paper += poly
    paper_mask = binary_closing(paper, selem=np.ones((10, 10)))  # избавляемся от шума и линии маркера

    empty_img = np.full(img.shape, 255, dtype=np.uint8)
    paper = empty_img * paper_mask
    poly = empty_img * poly  # преобразуем маску в изображение чтобы можно было работать с cv2

    paper = paper_edges(paper)  # находим границы листа
    poly = poly_edges(poly)  # находим границы многоугольника

    edges, matrix = coord_transformation(poly, paper)  # определяем координаты многоугольника относительно листа

    return paper, matrix, edges
