import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors


def R(theta):
    sin = np.sin(theta)
    cos = np.cos(theta)
    return np.array(
        [
            [cos, -sin, 0],
            [sin, cos, 0],
            [0, 0, 1],
        ]
    )


def dR(theta):
    """derivative of `R`"""
    sin = np.sin(theta)
    cos = np.cos(theta)
    return np.array(
        [
            [-sin, -cos, 0],
            [cos, -sin, 0],
            [0, 0, 0],
        ]
    )


def jacobian(theta, point):
    return np.hstack((np.eye(3), dR(theta) @ point))


def error(P, Q, x):
    pred = P @ R(x[-1][0]).T + x[:-1].T
    return pred - Q


def make_affine(X):
    ones = np.ones((X.shape[0], 1))
    return np.hstack((X, ones))


def ICP_leas_squares(P: np.ndarray, Q: np.ndarray, rot_center, theta_init, t_init):
    """
    theta_init: angle in rad
    """
    # 0. Apply initial guess
    # (R @ P.T).T = P @ R.T
    tr1 = np.eye(4)
    tr1[:2, 3] = rot_center
    tr2 = 2 * np.eye(4) - tr1
    tr3 = np.eye(4)
    tr3[:2, 3] = t_init
    rot = np.eye(4)
    rot[:3, :3] = R(theta_init)
    M = tr1 @ rot @ tr2 @ tr3
    # P = (make_affine(P) @ M.T)[:, :3]

    x = np.zeros((4, 1))
    x[:-1] = M[:3, 3][..., None]
    x[-1] = theta_init

    nbrs: NearestNeighbors = NearestNeighbors(
        n_neighbors=1,
        algorithm="kd_tree",
    ).fit(Q)

    P_cpy = P.copy()

    for _ in range(4):
        # 1. Find corresponding points
        _, corr_idx = nbrs.kneighbors(P_cpy)
        corr_Q = Q[corr_idx.ravel()]  # points corresponding to P

        E = error(P_cpy, corr_Q, x)[..., None]
        # J = np.array([jacobian(theta, p[..., None]) for p in P])

        # PERF: slowest part
        # 2. construct and solve least squares
        H = np.zeros((4, 4))
        g = np.zeros((4, 1))
        for e, p in zip(E, P):
            if np.linalg.norm(e) > 20:
                continue
            weight = 1  # / np.linalg.norm(e)
            J = jacobian(x[-1][0], p[..., None])
            H += weight * J.T @ J
            g += weight * J.T @ e

        dx = np.linalg.lstsq(H, -g, rcond=None)[0]
        x += dx
        # normalize angle
        # x[-1] = np.arctan2(np.sin(x[-1]), np.cos(x[-1]))

        P_cpy = P.copy() @ R(x[-1][0]).T + x[:-1].T

    affine_trans = np.hstack((R(-x[-1][0])[:-1, :-1], [x[1], x[0]]))

    # # temp plotting ----------------------------
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection="3d")
    # x, y, z = zip(*Q)
    # ax.scatter(x, y, z, c=z, cmap="inferno")
    # x, y, z = zip(*P_cpy)
    # ax.scatter(x, y, z, c=z, cmap="twilight")
    # ax.set_aspect("equal")
    # plt.show()
    # # ------------------------------------------

    return affine_trans


# def ICP_SVD(P: np.ndarray, Q: np.ndarray, rot_center, theta_init, x_init, y_init):
#     """
#     Computes ICP using SVD. P -> Q
#     P: 3d points to get the transformation for
#     Q: data to fit to
#     """
#
#     # 0. Apply initial guess
#     mu_p = np.array([*rot_center, 0])
#     P = np.array((P - mu_p) @ R(theta_init)) + mu_p
#
#     # 1. Center the data
#     mu_p = np.array([P.mean(axis=0)])
#     mu_q = np.array([Q.mean(axis=0)])
#     P_c = P - mu_p
#     Q_c = Q - mu_q
#
#     # 2. Find corresponding points
#     nbrs: NearestNeighbors = NearestNeighbors(
#         n_neighbors=1,
#         algorithm="kd_tree",
#     ).fit(Q_c)
#     _, corr_idx = nbrs.kneighbors(P_c)
#     Q = Q[corr_idx.ravel()]  # reorder to match P
#
#     # 3. Compute W
#     W = np.sum([q @ p.T for q, p in zip(Q_c[..., None], P_c[..., None])], axis=0)
#     print(W)
#
#     U, S, V = np.linalg.svd(W)
#     R = U @ V
#     # print(R)
#     t = mu_q.T - R @ mu_p.T
#
#     P = R @ P.T + t
#     P = P.T
#     # print(P)
#
#     # # temp plotting ----------------------------
#     # fig = plt.figure()
#     # ax = fig.add_subplot(111, projection="3d")
#     # x, y, z = zip(*Q)
#     # ax.scatter(x, y, z, c=z, cmap="inferno")
#     # x, y, z = zip(*P)
#     # ax.scatter(x, y, z, c=z, cmap="twilight")
#     # ax.set_aspect("equal")
#     # plt.show()
#     # # ------------------------------------------
