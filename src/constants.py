import numpy as np
import math

# from: https://github.com/xnx/penrose
psi = (math.sqrt(5) + 1) / 2
psi_inv = psi - 1

halfkite_height = math.sqrt(psi**2.0 - 0.25)
halfdart_height = math.sqrt(1.0 - (psi/2.0)**2.0)

# project point a on line defined by pq, find |px|:|pq| where x is the projection
def pointOfReflectionRatio(p: [np.float_], q: [np.float_], a: [np.float_]) -> [np.float_]:
    pq_dist = np.linalg.norm(q-p)
    return np.linalg.norm(p + (q - p) * ((q-p)*(a-p)) / pq_dist) / pq_dist

hk_reflection_CA = pointOfReflectionRatio(
    np.array([halfkite_height, 0.5]),
    np.array([0.0,0.0]),
    np.array([0.0,1.0])
)

hd_reflection_CB = pointOfReflectionRatio(
    np.array([psi*0.5, 0.0]),
    np.array([0.0, -halfdart_height]),
    np.array([-0.5*psi, 0.0])
)

VIEWPORT_UL = np.array([0.0338, 0.2541])
VIEWPORT_LR = np.array([0.6896, 0.7459])

# triangle rectangle intersection enum
TRI_RECT_WITHIN = 0
TRI_RECT_VTX_IN = 1
TRI_RECT_NTRSCT = 2
TRI_RECT_NVELOP = 3
TRI_RECT_DISJNT = 4