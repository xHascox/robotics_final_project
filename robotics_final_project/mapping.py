import time

import cv2
import icp
import numpy as np


def create_map(ep_robot):
    # Rectification
    # coordinates in image
    p = np.matrix(
        [
            [506, 522],
            [770, 519],
            [368, 650],
            [904, 644],
        ]
    )
    # coordinates in world
    q = np.matrix(
        [
            [500, 500],
            [600, 500],
            [500, 600],
            [600, 600],
        ]
    )

    H, _ = cv2.findHomography(p, q)
    height, width = 720, 1280
    mid_w = width // 2

    to_origin = np.eye(4)
    to_origin[:2, 3] = (-mid_w, -height)

    to_center = np.eye(4)
    to_center[:2, 3] = (1000, 1000)

    offset = np.eye(4)
    # offset[:2, 3] = (-10, 5)
    offset[:2, 3] = (0, 0)

    map = np.zeros((2000, 2000))
    ep_robot.camera.start_video_stream(display=True, resolution="720p")
    for yaw in np.arange(0, 360, 20):
        # get next frame
        ep_robot.gimbal.moveto(
            yaw=yaw, pitch=0, yaw_speed=90, pitch_speed=30
        ).wait_for_completed()

        again = True
        while again:
            try:
                frame = ep_robot.camera.read_cv2_image()
                again = False
            except Exception:
                time.sleep(1)

        # cut out the barrel
        frame[-100:, mid_w - 100 : mid_w + 100] = 0
        frame = cv2.warpPerspective(frame, H, (width, height))

        # first frame
        if yaw == 0:
            M = to_origin @ offset @ to_center
            M = np.hstack((np.eye(2), M[:2, 3][..., None]))
            map = cv2.warpAffine(frame, M, (map.shape[0], map.shape[1]))
        else:
            map_gr = cv2.cvtColor(map, cv2.COLOR_BGR2GRAY)
            frame_gr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # create a sample to match
            map_ri, map_ci = np.indices((map.shape[0], map.shape[1]))
            map_ri = map_ri.ravel()
            map_ci = map_ci.ravel()

            frame_ri, frame_ci = np.indices((frame.shape[0], frame.shape[1]))
            frame_ri = frame_ri.ravel()
            frame_ci = frame_ci.ravel()

            # transform matrices to a list of points [x, y, intensity] and filter out 0 values
            Q = np.stack((map_ri, map_ci, map_gr.ravel()), axis=-1)[map_gr.ravel() != 0]
            P = np.stack((frame_ri, frame_ci, frame_gr.ravel()), axis=-1)[
                frame_gr.ravel() != 0
            ]

            rng = np.random.default_rng(42)

            n = 10000
            Qsample = rng.choice(len(Q), n, replace=False)
            Psample = rng.choice(len(P), n, replace=False)

            rot = np.eye(4)
            theta = yaw * np.pi / 180
            rot[:3, :3] = icp.R(-theta)
            M_guess = to_center @ offset @ rot @ to_origin

            M = icp.ICP_leas_squares(
                P[Psample], Q[Qsample], M_guess, -theta, iterations=10, threshold=100
            )

            new_part = cv2.warpAffine(frame, M, (map.shape[0], map.shape[1]))
            _, mask = cv2.threshold(map_gr, 10, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            new_part = cv2.bitwise_and(new_part, new_part, mask=mask_inv)
            map = cv2.add(map, new_part)
            # cv2.imwrite("map_rt.png", map)
        time.sleep(1)

    ep_robot.camera.stop_video_stream()
    return map
