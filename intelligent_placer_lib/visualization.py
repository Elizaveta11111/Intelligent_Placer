from intelligent_placer_lib.fit import fit_in_corner, fit
from intelligent_placer_lib.fit import items as items_list
from intelligent_placer_lib.detect_item import items, use_sift
from intelligent_placer_lib.detect_polygon import binary, get_components, binary_closing, paper_edges, poly_edges, coord_transformation
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.patches
import numpy as np
from matplotlib import cm


def detect_polygon_and_show_steps(path_to_image):
    fig, ax = plt.subplots(1, 5, figsize=(12, 12))
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
    edges = coord_transformation(poly, paper)
    
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
    
    edges = coord_transformation(poly, paper) 
    
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


def detect_item(path_to_image):
    img = cv.imread(path_to_image)
    axes = plt.gca()
    axes.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    items_found = []
    for item_name in items:
        y1, y2, x1, x2 = items[item_name]
        item_img = cv.imread('objects/' + item_name + '.jpg')
        item_img = item_img[y1:y2, x1:x2]
        dst = use_sift(item_img, img)
        if dst is not None:
            rect = matplotlib.patches.Polygon(dst, fill=False)
            axes.add_patch(rect)
            plt.text(dst[0][0], dst[0][1], item_name, horizontalalignment="center")
            items_found.append(item_name)
    plt.show()
    

def drawPolygon(title, poly, item):
    plt.figure(figsize=(5, 5))
    axes = plt.gca()
    axes.set_aspect("equal")
    axes.set_xlim([-50, 210])
    axes.set_ylim([-50, 297])
    axes.set_title(title)
    axes.set_axis_off()
    polygon = matplotlib.patches.Polygon(poly, fill=False, closed=True, linewidth=2, color='r')
    axes.add_patch(polygon)
    polygon = matplotlib.patches.Polygon(item, fill=False, closed=True, linewidth=2, color='g')
    axes.add_patch(polygon)

    
def drawPolygons(title, item, poly, new_item):
    plt.figure(figsize=(5, 5))
    axes = plt.gca()
    axes.set_aspect("equal")
    axes.set_xlim([-50, 210])
    axes.set_ylim([-50, 297])
    axes.set_title(title)
    axes.set_axis_off()
    polygon = matplotlib.patches.Polygon(poly, fill=False, closed=True, linewidth=2, color='b')
    axes.add_patch(polygon)
    polygon = matplotlib.patches.Polygon(new_item, fill=False, closed=True, linewidth=2, color='r')
    axes.add_patch(polygon)
    polygon = matplotlib.patches.Polygon(item, fill=False, closed=True, linewidth=2)
    axes.add_patch(polygon)
    
    
def variants(poly, name):
    for item in items_list[name]:
        for i in range(len(poly)):
            inside, new_item, new_poly = fit_in_corner(poly, item, i)
            drawPolygons(inside, item, new_poly, new_item)
    plt.show()
    

def result(poly, name):
    inside, item, poly = fit(poly, name)
    drawPolygon(inside, item, poly)
