import cv2 as cv
import numpy as np
from skimage.measure import regionprops
from skimage.measure import label as sk_measure_label
from skimage.morphology import binary_closing, binary_opening
from intelligent_placer_lib.decide import decide
from intelligent_placer_lib.utility import dist

items_order = ['yellow_scissors', 'book', 'tool', 'mascara', 'scissors', 'stapler', 'tape', 'lighter', 'toy', 'heart']

# находит маски предметов на бинаризованном изображении
def get_largest_components(mask):
    labels = sk_measure_label(mask)  # разбиение маски на компоненты связности
    props = regionprops(labels)  # нахождение свойств каждой области
    areas = [prop.area for prop in props]  # нас интересуют площади компонент связности
    items_masks = []
    for i in range(len(areas)):  # выбираем достаточно большие компоненты, чтобы отсечь шум
        if areas[i] > 1000:
            items_masks.append(labels == i + 1)
    return items_masks


# определяет верхний правый и нижний левый угол четырехугольника, расширив границы на k пикселей
def get_corners(points):
    k = 2
    bottom_left = (int(min(points[:, 0]) - k), int(min(points[:, 1]) - k))
    top_right = (int(max(points[:, 0]) + k), int(max(points[:, 1]) + k))
    return top_right, bottom_left


# находит наименьший четырехугольник ограничивающий переданную маску
def find_box(obj_mask):
    empty_img = np.full(obj_mask.shape, 255, dtype=np.uint8)
    obj = empty_img * obj_mask  # переводим маску в rgb
    contours, hierarchy = cv.findContours(obj, 1, 2)  # находим контуры на изображении
    max_area = 0
    for cnt in contours:  # находим контур с наибольшей площадью
        rect = cv.minAreaRect(cnt)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        area = dist(box[0], box[1]) * dist(box[1], box[2])
        if area > max_area:
            max_box = box  # находим наименьший ограничивающий четырехугольник
    return max_box


# по координатам углов листа возвращает его маску
def get_paper_mask(paper_points, mask_shape):
    paper = np.zeros(mask_shape, np.uint8)  # создаем пустое изобажение
    corn1, corn2 = get_corners(paper_points)  # находим правый верхний и левый нижний углы
    cv.rectangle(paper, corn1, corn2, (255, 255, 255), -1)  # рисуем прямоугольник на изображении
    return cv.cvtColor(paper, cv.COLOR_BGR2GRAY)


# определяет порядок размещения объектов в многоугольнике
def sort(items):
    item_list = []
    for item in items_order:
        if item in items:
            item_list.append(item)
    return item_list


def detect_item(path_to_image, paper_points, transformation_matrix):
    img = cv.imread(path_to_image)  # входная фоторафия
    background = cv.imread('objects/background.jpg')  # фон
    paper = get_paper_mask(paper_points, img.shape)  # маска листа

    items_on_img = img - background  # вычитаем из изображения фон
    items_on_img = items_on_img - (items_on_img > 200) * items_on_img  # вычитаем участки с низкой интенсивностью
    items_mask = (items_on_img > 100)  # создаем маску
    items_mask = (items_mask[..., 0] + items_mask[..., 1] + items_mask[..., 2]) * ~paper  # складываем rgb компоненты и
    # удаляем с маски лист бумаги
    items_mask = binary_closing(items_mask, selem=np.ones((5, 5)))  # расширяем границы, чтобы детали предмета не
    items_mask = binary_opening(items_mask, selem=np.ones((5, 5)))  # делили его на части

    items_masks = get_largest_components(items_mask)  # получаем маски предметов

    items_found = []
    for item_mask in items_masks:
        # для каждой маски определяем ограничивающий прямоугольник
        item_box = find_box(item_mask)
        corn2, corn1 = get_corners(item_box)
        item_img = img[corn1[1]:corn2[1], corn1[0]:corn2[0]]
        item_mask = item_mask[corn1[1]:corn2[1], corn1[0]:corn2[0]]
        # определяем предмет по размерам и цвету
        item = decide(item_box, transformation_matrix, item_mask, item_img)
        if item is not None and item not in items_found:
            items_found.append(item)
    return sort(items_found)  # возвращаем предметы в порядке их приоритета
