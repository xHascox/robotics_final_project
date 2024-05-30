import timeit

import cv2
import numpy as np
from icp import ICP_leas_squares


def show_img(img):
    cv2.imshow("Title", img)

    while cv2.getWindowProperty("Title", cv2.WND_PROP_VISIBLE) >= 1:
        key = cv2.waitKey(100)
        if (key & 0xFF) == ord("q"):
            cv2.destroyAllWindows()
            break


def rotate_img(img, angle):
    height, width = img.shape[:2]
    mid = width // 2

    M = cv2.getRotationMatrix2D((mid, height), angle=angle, scale=1)

    # translation
    # t_x
    M[0, 2] += -30
    # t_y
    M[1, 2] += 60
    # print(M)

    return cv2.warpAffine(img, M, (width, height))


def main():
    # Rectification
    # More points result in greater distortion -> bad :(
    # coordinates in image
    p = np.matrix(
        [
            [506, 522],
            [770, 519],
            [368, 650],
            [904, 644],
            # [374, 482],
            # [572, 459],
            # [241, 524],
            # [702, 459],
            # [833, 457],
            # [899, 477],
        ]
    )
    # coordinates in world
    q = np.matrix(
        [
            [500, 500],
            [600, 500],
            [500, 600],
            [600, 600],
            # [400, 400],
            # [500, 300],
            # [400, 500],
            # [600, 300],
            # [700, 300],
            # [700, 400],
        ]
    )

    H, _ = cv2.findHomography(p, q)

    front = cv2.imread("./straight.png")
    right = cv2.imread("./right_gimbal.png")

    height, width, _ = front.shape

    start = timeit.default_timer()
    # 0 is "unknown"
    # cut out the barrel
    mid_w = width // 2
    front[-100:, mid_w - 100 : mid_w + 100] = 0
    right[-100:, mid_w - 100 : mid_w + 100] = 0

    front = cv2.warpPerspective(front, H, (width, height))
    right = cv2.warpPerspective(right, H, (width, height))

    front_img = front.copy()
    right_img = right.copy()

    # mask extra area
    # front[:300, :] = 0
    # right[:300, :] = 0
    # front[:, : mid_w - 200] = 0
    # right[:, mid_w:] = 0

    # NOTE: use gray-scale (3D) to find the transformation, apply to full color images
    front = cv2.cvtColor(front, cv2.COLOR_BGR2GRAY)
    # _, front = cv2.threshold(front, 190, 255, cv2.THRESH_BINARY)
    right = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)
    # _, right = cv2.threshold(right, 190, 255, cv2.THRESH_BINARY)

    # TODO: use angle from odometry
    angle = -45

    # create a sample to match
    ri, ci = np.indices((height, width))
    ri = ri.ravel()
    ci = ci.ravel()
    # transform matrices to a list of points [x, y, intensity] and filter out 0 values
    Q = np.stack((ri, ci, front.ravel()), axis=-1)[front.ravel() != 0]
    P = np.stack((ri, ci, right.ravel()), axis=-1)[right.ravel() != 0]

    rng = np.random.default_rng(42)

    n = 10000
    Qsample = rng.choice(len(Q), n, replace=False)
    Psample = rng.choice(len(P), n, replace=False)

    M = ICP_leas_squares(
        P[Psample], Q[Qsample], (mid_w, height), angle * np.pi / 180, (100, 60)
    )
    duration = timeit.default_timer() - start
    print(f"Took: {duration:.4f}s")

    print(M)
    img = cv2.warpAffine(right_img, M, (width, height))
    # right = cv2.warpAffine(right, M, (width, height))
    # show_img(fron)
    # right = rotate_img(right, angle)

    cv2.imwrite("img/font_top.png", front_img + img)
    # cv2.imwrite("img/font_top.png", front + right)


if __name__ == "__main__":
    main()
