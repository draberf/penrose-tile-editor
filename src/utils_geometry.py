import numpy as np
import src.constants as cts

# from https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def pointInTriangle(a: [np.float_], b: [np.float_], c: [np.float_], x: [np.float_]) -> bool:
    barycentrics = [np.cross(t2-t1, x-t1) for (t1, t2) in [(a,b), (b,c), (c,a)]]
    return all([x < 0 for x in barycentrics]) or all([x > 0 for x in barycentrics])


# return relative positions of a triangle ABC and an axis-aligned rectangle UL (upper-left), LR (lower-right)
def triangleRectanglePosition(A: [np.float_], B: [np.float_], C: [np.float_], UL: [np.float_], LR: [np.float_]) -> int:
    
    within = [
        vertex[0] > UL[0] and
        vertex[1] > UL[1] and
        vertex[0] < LR[0] and
        vertex[1] < LR[1] for vertex in [A,B,C]]
    
    # triangle is contained within rectangle
    if all(within): return cts.TRI_RECT_WITHIN
    
    # 1-2 vertices are contained within rectangle
    if any(within): return cts.TRI_RECT_VTX_IN

    UR = np.array([LR[0], UL[1]])
    LL = np.array([UL[0], LR[1]])

    
    # vvv  no triangle vertices are within  vvv
    for (t1, t2) in [(A,B), (B,C), (C,A)]:
        for (r1, r2) in [(UL, LL), (LL, LR), (LR, UR), (UR, UL)]:
            if intersect(t1, t2, r1, r2): return cts.TRI_RECT_NTRSCT

    # check if square contained within
    for r in [UL, LL, LR, UR]:
        barycentrics = [np.cross(t2-t1, r-t1) for (t1, t2) in [(A,B), (B,C), (C,A)]]
        if all([x < 0 for x in barycentrics]): continue
        if all([x > 0 for x in barycentrics]): continue
        return cts.TRI_RECT_DISJNT

    return cts.TRI_RECT_NVELOP

if __name__=="__main__":
    ul = np.array([-1.0, -1.0])
    lr = np.array([ 1.0,  1.0])
    
    a = np.array([-2.0, -10.0])
    b = np.array([-2.0,   2.0])
    c = np.array([10.0,   2.0])

    print(triangleRectanglePosition(a, b, c, ul, lr))