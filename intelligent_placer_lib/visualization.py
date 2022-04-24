from intelligent_placer_lib.fit import fit_in_corner
from intelligent_placer_lib.fit import items as items_list
from intelligent_placer_lib.place_item import place_item
from intelligent_placer_lib.decide import decide
from intelligent_placer_lib.detect_item import find_box, get_largest_components, get_corners, get_paper_mask, sort
from intelligent_placer_lib.detect_polygon import binary, get_components, paper_edges, poly_edges, coord_transformation
from intelligent_placer_lib.utility import apply_transformation
from intelligent_placer_lib.update_polygon import update_polygon
from skimage.morphology import binary_closing, binary_opening
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.patches
import numpy as np
from matplotlib import cm

def detect_polygon_and_show_steps(path_to_image):
    fig, ax = plt.subplots(1, 5, figsize=(15, 15))
    [axi.set_axis_off() for axi in ax.ravel()]
    
    img = cv.imread(path_to_image, cv.IMREAD_GRAYSCALE)
    
    mask = binary(img)
    paper, poly = get_components(mask)
    paper += poly
    paper_mask = binary_closing(paper, selem=np.ones((10, 10)))
    
    ax[0].imshow(mask, cmap=cm.gray)
    ax[0].set_title('Binary mask')
    ax[1].imshow(paper_mask, cmap=cm.gray)
    ax[1].set_title('Paper mask')
    ax[2].imshow(poly, cmap=cm.gray)
    ax[2].set_title('Polygon mask')
    
    black = np.full(img.shape, 255, dtype=np.uint8)
    paper = paper_edges(black * paper_mask)
    poly = poly_edges(black * poly)
    edges, _ = coord_transformation(poly, paper)
    
    paper = matplotlib.patches.Polygon(paper, fill=False, color='r')
    poly = matplotlib.patches.Polygon(poly, fill=False, color='g')
    
    ax[3].imshow(img, cmap=cm.gray)
    ax[3].add_patch(paper)
    ax[3].add_patch(poly)
    ax[3].set_title('Edges')
    
    
    n = len(edges)
    edges = matplotlib.patches.Polygon(edges, fill=False, color='g')
    ax[4].add_patch(edges)
    ax[4].set_xlim([0, 210])
    ax[4].set_ylim([0, 297])
    ax[4].set_aspect("equal")
    plt.title('edges num = ' + str(n))
    plt.show()

    
def detect_polygon(path_to_image):
    img_col = cv.imread(path_to_image)
    img = cv.imread(path_to_image, cv.IMREAD_GRAYSCALE)
    
    mask = binary(img)
    paper, poly = get_components(mask)
    paper += poly 
    paper_mask = binary_closing(paper, selem=np.ones((10, 10))) 
    
    black = np.full(img.shape, 255, dtype=np.uint8) 
    paper = black * paper_mask
    poly = black * poly 
    
    paper = paper_edges(paper) 
    poly = poly_edges(poly)
    
    edges, _ = coord_transformation(poly, paper) 
    
    n = len(edges)
    fig, ax = plt.subplots(1, 2)
    [axi.set_axis_off() for axi in ax.ravel()]
    ax[0].imshow(cv.cvtColor(img_col, cv.COLOR_BGR2RGB))
    edges = matplotlib.patches.Polygon(edges, fill=False, color='r')
    ax[1].add_patch(edges)
    ax[1].set_xlim([0, 210])
    ax[1].set_ylim([0, 297])
    ax[1].set_aspect("equal")
    plt.title('edges num = ' + str(n))
    plt.show()
    
    return edges


def get_items_masks(path_to_image, paper_points):
    img = cv.imread(path_to_image)
    background = cv.imread('objects/background.jpg')
    paper = get_paper_mask(paper_points, img.shape)

    print('Исходное изображение')
    plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

    items_on_img = img - background
    print('Вычли фотографию фона')
    plt.imshow(cv.cvtColor(items_on_img, cv.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

    items_on_img = items_on_img - (items_on_img > 200) * items_on_img
    print('Убрали пиксели с высокой интенсивностью')
    plt.imshow(cv.cvtColor(items_on_img, cv.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

    items_mask = (items_on_img > 100)
    items_mask = (items_mask[..., 0] + items_mask[..., 1] + items_mask[..., 2]) * ~paper
    print('Получили маску для каждого rgb слоя, бинаризовав по порогу 100. Сложили все слои, таким образом получив маску предметов на изображении. Далее с маски убран лист, его координаты известны из распознавания многоугольника.')
    plt.imshow(items_mask, cmap='gray')
    plt.axis('off')
    plt.show()
    items_mask = binary_closing(items_mask, selem=np.ones((5, 5)))
    items_mask = binary_opening(items_mask, selem=np.ones((5, 5)))

    items_masks = get_largest_components(items_mask)
    colored_items = np.zeros(img.shape, np.uint8)
    for item_mask in items_masks:
        colored_mask = np.full(img.shape, list(np.random.choice(range(256), size=3)), dtype=np.uint8)
        colored_mask[:, :, 0] *= item_mask
        colored_mask[:, :, 1] *= item_mask
        colored_mask[:, :, 2] *= item_mask
        colored_items += colored_mask
    print('С помощью анализа компонент связности нашли области с достаточно большой площадью, получив маску для каждого предмета по отдельности.')
    plt.imshow(cv.cvtColor(colored_items, cv.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()


def detect_item(path_to_image, paper_points, transformation_matrix, axes):
    img = cv.imread(path_to_image)
    background = cv.imread('objects/background.jpg')
    paper = get_paper_mask(paper_points, img.shape)

    items_on_img = img - background
    items_on_img = items_on_img - (items_on_img > 200) * items_on_img
    items_mask = (items_on_img > 100)
    items_mask = (items_mask[..., 0] + items_mask[..., 1] + items_mask[..., 2]) * ~paper
    items_mask = binary_closing(items_mask, selem=np.ones((5, 5)))
    items_mask = binary_opening(items_mask, selem=np.ones((5, 5)))

    items_masks = get_largest_components(items_mask)
    items_found = []
    
    for item_mask in items_masks:
        item_box = find_box(item_mask)
        corn2, corn1 = get_corners(item_box)
        x1 = corn1[0]
        x2 = corn2[0]
        y1 = corn1[1]
        y2 = corn2[1]
        item = decide(item_box, transformation_matrix, item_mask[y1:y2, x1:x2], img[y1:y2, x1:x2])
        if item is not None:
            if  item not in items_found:
                items_found.append(item)
            box = matplotlib.patches.Polygon(item_box, fill=False, closed=True, linewidth=2, color='b')
            axes.add_patch(box)
            axes.text(x1, y1, item, color='b')
            

    axes.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    
    return sort(items_found)
    
def variants(poly, name):
    for item in items_list[name]:
        if len(item) == 0:
            break
        for i in range(len(poly)):
            inside, new_item, new_poly, _, _, _ = fit_in_corner(poly, item, i)
            plt.figure(figsize=(5, 5))
            axes = plt.gca()
            axes.set_aspect("equal")
            axes.set_xlim([-50, 210])
            axes.set_ylim([-50, 297])
            axes.set_title(inside)
            axes.set_axis_off()
            polygon = matplotlib.patches.Polygon(item, fill=False, closed=True, linewidth=2)
            axes.add_patch(polygon)
            polygon = matplotlib.patches.Polygon(new_poly, fill=False, closed=True, linewidth=2, color='b')
            axes.add_patch(polygon)
            polygon = matplotlib.patches.Polygon(new_item, fill=False, closed=True, linewidth=2, color='r')
            axes.add_patch(polygon)
            

def next_poly_variants(poly, name):
    for item in items_list[name]:
        if len(item) == 0:
            break
        for i in range(len(poly)):
            inside, new_item, poly, points_on_sides_list, points_assignment, _ = fit_in_corner(poly, item, i)
            if inside:
                new_poly, _ = update_polygon(poly, new_item, points_on_sides_list, points_assignment, name)
                plt.figure(figsize=(5, 5))
                axes = plt.gca()
                axes.set_axis_off()
                axes.set_aspect("equal")
                axes.set_xlim([-50, 210])
                axes.set_ylim([-50, 297])
                polygon = matplotlib.patches.Polygon(poly, fill=True, closed=True, linewidth=2, color='b')
                axes.add_patch(polygon)
                polygon = matplotlib.patches.Polygon(new_poly, fill=False, closed=True, linewidth=2)
                axes.add_patch(polygon)
                plt.show()     
          
         
def result(polygon, name):
    new_polygon, item, matrix = place_item(polygon, name)
    if item is not None:
        plt.figure(figsize=(5, 5))
        axes = plt.gca()
        axes.set_aspect("equal")
        axes.set_xlim([-50, 210])
        axes.set_ylim([-50, 297])
        polygon = matplotlib.patches.Polygon(apply_transformation(polygon, matrix), fill=True, closed=True, linewidth=2, color='b')
        axes.add_patch(polygon)
        polygon = matplotlib.patches.Polygon(new_polygon, fill=False, closed=True, linewidth=2)
        axes.add_patch(polygon)
        plt.show()
        
        
def move_all(first_poly, poly, items, matrix):
    first_poly = apply_transformation(first_poly, matrix)
    poly = apply_transformation(poly, matrix)
    items = [apply_transformation(item, matrix) for item in items]
    return first_poly, poly, items


def place_items(polygon, items_names, axes):
    first_poly = polygon
    items = []
    ans = True
    for i in range(len(items_names)):
        name = items_names[i]
        polygon, item, matrix = place_item(polygon, name)
        if polygon is None:
            ans = False
            break
        first_poly, _, items = move_all(first_poly, polygon, items, matrix)
        items.append(item)
    if len(items):
        axes.set_aspect("equal")
        axes.set_title(ans)
        patch = matplotlib.patches.Polygon(first_poly, fill=True, closed=True, linewidth=2, color='b')
        axes.add_patch(patch)
        for i in range(len(items)):
            item = items[i]
            patch = matplotlib.patches.Polygon(item, fill=False, closed=True, linewidth=2)
            plt.text(item[0][0], item[0][1], items_names[i])
            axes.add_patch(patch)
            axes.set_xlim([item[0][0] - 150, item[0][0] + 150])
            axes.set_ylim([item[0][1] - 150, item[0][1] + 200])
    return ans