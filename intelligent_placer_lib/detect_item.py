import cv2 as cv
import numpy as np

items = {'book': [330, 700, 100, 580],
         'lighter': [360, 650, 300, 410],
         'mascara': [260, 700, 310, 410]}


def use_sift(img1, img2):
    MIN_MATCH_COUNT = 10
    height, width, channels = img1.shape

    sift = cv.SIFT_create()

    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1, des2, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.5 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
        if M is not None:
            pts = np.float32([[0, 0], [0, height], [width, height], [width, 0]]).reshape(-1, 1, 2)
            dst = cv.perspectiveTransform(pts, M)
            dst = np.reshape(dst, (4, 2))
            return dst
    return None


def detect_item(path_to_image):
    img = cv.imread(path_to_image)
    items_found = []
    for item_name in items:
        y1, y2, x1, x2 = items[item_name]
        item_img = cv.imread('objects/' + item_name + '.jpg')
        item_img = item_img[y1:y2, x1:x2]
        dst = use_sift(item_img, img)
        if dst is not None:
            items_found.append(item_name)
    return items_found
