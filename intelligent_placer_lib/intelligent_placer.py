from intelligent_placer_lib import detect_polygon, detect_item, place_item


def check_image(path_to_image):
    paper, matrix, poly = detect_polygon.detect_polygon(path_to_image)
    items = detect_item.detect_item(path_to_image, paper, matrix)
    return place_item.place_items(poly, items)