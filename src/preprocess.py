import cv2
import numpy as np

def load_images(paths):
    imgs = []
    for p in paths:
        img = cv2.imread(p, 0)
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        imgs.append(img)

    h = min(i.shape[0] for i in imgs)
    w = min(i.shape[1] for i in imgs)
    imgs = [i[:h, :w] for i in imgs]

    return imgs


def split_into_strips(img, strip_height=2500):
    return [img[i:i+strip_height, :] for i in range(0, img.shape[0], strip_height)]


def multiscale_images(img):
    return {
        "original": img,
        "medium": cv2.GaussianBlur(img, (9,9), 0),
        "large": cv2.GaussianBlur(img, (21,21), 0)
    }
