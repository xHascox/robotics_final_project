import cv2
import numpy as np


def show_img(img):
    cv2.imshow("Title", img)

    while cv2.getWindowProperty("Title", cv2.WND_PROP_VISIBLE) >= 1:
        key = cv2.waitKey(100)
        if (key & 0xFF) == ord("q"):
            cv2.destroyAllWindows()
            break


# img = cv2.imread("./right_gimbal.png")
img = cv2.imread("./straight.png")
print(img.shape)

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

th3 = cv2.adaptiveThreshold(
    img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
)
inv = 255 - th3

# # kernel = np.ones((5, 5))
# kernel = np.matrix(
#     [
#         [0, 0, 1, 0, 0],
#         [0, 1, 1, 1, 0],
#         [1, 1, 1, 1, 1],
#         [0, 1, 1, 1, 0],
#         [0, 0, 1, 0, 0],
#     ],
#     dtype=np.uint8,
# )

# kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
# kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# inv = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, kernel_close)
# inv = cv2.morphologyEx(inv, cv2.MORPH_OPEN, kernel_open)

# NOTE: RIP lines
# lines = cv2.HoughLines(
#     inv,
#     rho=1,
#     theta=np.pi / 180,
#     threshold=200,
# )

# # print(lines)
# print(len(lines))
#
# for rho, theta in lines.squeeze():
#     a = np.cos(theta)
#     b = np.sin(theta)
#     x0 = a * rho
#     y0 = b * rho
#
#     pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
#     pt2 = (int(x0 - 2000 * (-b)), int(y0 - 2000 * (a)))
#     cv2.line(img, pt1, pt2, (255, 0, 0), 1, cv2.LINE_AA)

# for x0, y0, x1, y1 in lines.squeeze():
#     cv2.line(img, (x0, y0), (x1, y1), (255, 0, 0), 2, cv2.LINE_AA)


def extract_keypoints(img):
    # create mask to hide the nozzle
    # FIXME: the mask probs too big
    height, width, _ = img.shape
    mask = np.ones((height, width), dtype=np.uint8)
    mid = width // 2
    mask[-200:, mid - 200 : mid + 200] = 0

    # TODO: better feature prep
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img = cv2.adaptiveThreshold(
    #     img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    # )

    sift = cv2.SIFT_create()
    keypoints, features = sift.detectAndCompute(img, mask=mask)
    return keypoints, features


def main():
    # Rectification
    # TODO: add more points for better accuracy
    # coordinates in image
    p = np.matrix([[506, 522], [770, 519], [368, 650], [904, 644]])
    # coordinates in world
    q = np.matrix([[500, 500], [600, 500], [500, 600], [600, 600]])

    H, _ = cv2.findHomography(p, q)

    # out = cv2.warpPerspective(img, H, (img.shape[1], img.shape[0]))
    front = cv2.imread("./straight.png")
    right = cv2.imread("./right_gimbal.png")

    height, width, _ = front.shape

    front = cv2.warpPerspective(front, H, (width, height))
    right = cv2.warpPerspective(right, H, (width, height))

    front_key, front_feat = extract_keypoints(front)
    right_key, right_feat = extract_keypoints(right)

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    best_matches = bf.match(front_feat, right_feat)

    match = cv2.drawMatches(
        front,
        front_key,
        right,
        right_key,
        best_matches,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )

    # extract coordinates
    front_key = np.float32([kp.pt for kp in front_key])
    right_key = np.float32([kp.pt for kp in right_key])

    mpoints_front = np.float32([front_key[m.queryIdx] for m in best_matches])
    mpoints_right = np.float32([right_key[m.trainIdx] for m in best_matches])

    H_stitch, _ = cv2.findHomography(mpoints_right, mpoints_front, cv2.RANSAC)
    # H_stitch[2] = [0, 0, 1]
    print(H_stitch)

    out = cv2.warpPerspective(right, H_stitch, (width * 2, height * 2))

    # show_img(inv)
    # show_img(out)
    # show_img(img_gray)
    show_img(front)

    cv2.imwrite("img/font_top.png", front)


if __name__ == "__main__":
    main()
