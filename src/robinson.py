from src.constants import psi, psi_inv, halfkite_height, VIEWPORT_LR, VIEWPORT_UL
import src.constants as cts
from src.utils_geometry import triangleRectanglePosition, pointInTriangle

import numpy as np

import xml.etree.ElementTree as ET



def getSuperneighborhood(type1: str, edge: int, type2: str) -> [(int, int, int)]:

    if type1 not in ["halfkite", "halfdart"]:
        raise ValueError(f"Unrecognized Robinson type '{type1}' passed as type1")
    if type2 not in ["halfkite", "halfdart"]:
        raise ValueError(f"Unrecognized Robinson type '{type2}' passed as type2")
    if edge < 1 or edge > 4:
        raise ValueError(f"Invalid edge value '{edge}'")

    if type1 == "halfkite":
        if edge == 1:
            return [(1, 1, 2)]
        if edge == 2:
            if type2 == "halfkite":
                return [(2, 2, 2), (3, 3, 4)]
            else:
                return [(2, 2, 2), (3, 1, 4)]
        if edge == 3:
            # TODO: check for error if type2 = halfkite
            return [(1, 1, 1), (3, 3, 2)]            
        
    if type1 == "halfdart":
        if edge == 1:
            return [(1, 1, 2)]
        if edge == 2:
            if type2 == "halfkite":
                return [(1, 3, 4), (2, 2, 2)]
            else:
                return [(1, 1, 4), (2, 2, 2)]
        if edge == 4:
            return [(2, 2, 3)]
        
    raise ValueError(f"Unhandled combination of arguments ({type1}, {type2}, {edge})")

def robinsonFactory(type: str, a: [np.float_], b: [np.float_], c: [np.float_]) -> 'Robinson':
    
    if type == "halfkite": return HalfKite(a, b, c)
    if type == "halfdart": return HalfDart(a, b, c)
    
    return Robinson(a, b, c)

def reflectedCoords(type: str, a: [np.float_], b: [np.float_], c: [np.float_]) -> [[np.float_]]:

    if type == "halfkite":
        x = c + cts.hk_reflection_CA*(a - c)
        return [a, x, c]
    if type == "halfdart":
        x = c + cts.hd_reflection_CB*(b - c)
        return [x, b, c]
    
    return [a, b, c]

class Robinson:

    next_id = 0
    

    def __init__(self, a: [np.float_], b: [np.float_], c: [np.float_]):
        self.a, self.b, self.c = a, b, c
        self.neighbors = [None,None,None,None]
        self.leaf = True
        self.parent = None
        self.children = [None, None, None]
        self.id = "0"
        self.index = -1
        self.cls = ""
        self.level = 0
        self.skip_window = False
        self.children_blueprint = []

    def inflate(self, window=None):
        if self.leaf:
            self._inflate(window)
        else:
            for child in self.children:
                if not child: continue
                child.inflate(window)
    
    def _inflate(self, window=None):
        self.leaf = False
        coords = [x[0] for x in self.children_blueprint]
        types  = [x[1] for x in self.children_blueprint]
        nbs    = [x[2] for x in self.children_blueprint]
        
        for i, (type, (a, b, c)) in enumerate(zip(types, coords)):
            
            # test if coords are wholly within rectangle
            if window and not self.skip_window:
                ul = window[0]
                lr = window[1]
                intersection = triangleRectanglePosition(a, b, c, ul, lr)
                if intersection == cts.TRI_RECT_WITHIN:
                    self.skip_window = True
                elif intersection == cts.TRI_RECT_DISJNT:
                    # test if reflected is within:
                    ra, rb, rc = reflectedCoords(type, a, b, c)
                    if triangleRectanglePosition(ra, rb, rc, ul, lr) == cts.TRI_RECT_DISJNT:
                        # trash child triangle
                        continue

            # add triangle
            self.children[i] = robinsonFactory(type, a, b, c)
            self.children[i].parent = self
            self.children[i].index = i + 1
            self.children[i].id = f"{self.id}-{i+1}"
            if self.skip_window: self.children[i].skip_window = True
        
        # set neighbors
        for child, neighbors in zip(self.children, nbs):
            if not child: continue
            for edge, neighbor in neighbors:
                if not self.children[neighbor]: continue
                child.neighbors[edge] = self.children[neighbor]

    def findNeighbors(self):
        
        if not self.leaf:
            for child in self.children:
                if not child: continue
                child.findNeighbors()
            return
        
        if not self.parent: return

        for edge_index, super_neighbor in enumerate(self.parent.neighbors):
            if not super_neighbor: continue
            edge = edge_index + 1
            try:
                neighbor_list = getSuperneighborhood(self.parent.cls, edge, super_neighbor.cls)
            except:
                print(self.parent.neighbors)
                raise
            for my_index, my_neighbor_index, edge_type in neighbor_list:
                if my_index != self.index: continue
                self.neighbors[edge_type-1] = super_neighbor.children[my_neighbor_index-1]
    
    def getAllLeaves(self) -> ['Robinson']:
        if self.leaf: return [self]
        leaves = []
        for child in self.children:
            if not child: continue
            leaves.extend(child.getAllLeaves())
        return leaves

    def getMirror(self) -> 'Robinson':
        raise TypeError("Base Robinson class triangles don't have mirrors")

class HalfDart(Robinson):
    # A > B >>>> C >> A
    # AB : BC : CA = 1 : 1 : psi

    def __init__(self, a: [np.float_], b: [np.float_], c: [np.float_]):
        super().__init__(a, b, c)
        self.cls = "halfdart"
        # add children coords and neighborhoods here
        # D on CA such that CD : DA = psi : 1
        # new triangles:
        #  - BDA half-dart
        #  - BDC half-kite
        d = c + psi_inv*(a-c)
        self.children_blueprint = [
            ((b, d, a), "halfdart", [(0, 1)]),
            ((b, d, c), "halfkite", [(0, 0)]),
        ]

    def getMirror(self) -> 'Robinson':
        return self.neighbors[3]

class HalfKite(Robinson):
    # A > B >> C >>> A
    # AB : BC : CA = 1 : psi : psi

    def __init__(self, a: [np.float_], b: [np.float_], c: [np.float_]):
        super().__init__(a, b, c)
        self.cls = "halfkite"
        # D on BC such that BD : DC = psi : 1
        # E on CA such that CE : EA = psi : 1
        # new triangles:
        #  - EAB half-kite
        #  - EDB half-kite
        #  - EDC half-dart
        d = b + psi_inv*(c-b)
        e = c + psi_inv*(a-c)
        self.children_blueprint = [
            ((e, a, b), "halfkite", [(2, 1)]),
            ((e, d, b), "halfkite", [(2, 0), (0, 2)]),
            ((e, d, c), "halfdart", [(0, 1)])
        ]

    def getMirror(self) -> 'Robinson':
        return self.neighbors[2]

class P2:

    def __init__(self, levels: int):
        self.triangle = HalfKite(
            np.array([0.0, 0.0]),
            np.array([0.0, 1.0]),
            np.array([halfkite_height, 0.5])
        )
        
        for _ in range(levels):
            self.triangle.inflate(window=(VIEWPORT_UL, VIEWPORT_LR))
            self.triangle.findNeighbors()

def searchSmallestAtPoint(triangle: Robinson, x: [np.float_]) -> int:
    if pointInTriangle(triangle.a, triangle.b, triangle.c, x): 

        if triangle.leaf: return triangle.id
        else:
            for child in triangle.children:
                if not child: continue
                if (id := searchSmallestAtPoint(child, x)) != -1: return id

    return -1

def getPaths(triangle: Robinson):
    if not triangle.leaf:
        paths = []
        for child in triangle.children:
            if child: paths.extend(getPaths(child))
        return paths
    elem = ET.Element('path')
    elem.set("d", f"M {triangle.a[0]} {triangle.a[1]} L {triangle.b[0]} {triangle.b[1]} {triangle.c[0]} {triangle.c[1]} z")
    elem.set("class", triangle.cls)
    elem.set("id", "id"+str(triangle.id))
    elem.set("fill", f"rgb({255*triangle.level} {255*triangle.level} {255*triangle.level})")
    return [elem]

def getByID(triangle: Robinson, id):
    if triangle.id == id: return triangle
    for child in triangle.children:
        if not child: continue
        if (maybe := getByID(child, id)): return maybe
    return None

def propagateFromID(level, visited: [Robinson], queue: [Robinson]):
    if level < 0.03: return
    if queue == []: return
    new_queue = []
    for current in queue:
        current.level = level
        visited.append(current)
        for neighbor in current.neighbors:
            if not neighbor: continue
            if neighbor in visited: continue
            new_queue.append(neighbor)
    propagateFromID(level*0.9, visited, new_queue)

if __name__=="__main__":

    p2 = P2(3)
    triangle = p2.triangle

    i = 0
    while (t := getByID(triangle, i)):
        break
        print(i, t.cls)
        for ii, neighbor in enumerate(t.neighbors):
            if neighbor: print("-", ">"*(ii+1), neighbor.id)
        i+=1

    id = searchSmallestAtPoint(triangle, np.array([0.1,0.5]))
    getByID(triangle, id).level = 1

    #print(triangle.id)
    #print(getByID(triangle, 10945))
    # 8 levels -- 4180 triangles
    # 9 levels -- 10945 triangles

    #propagateFromID(1, [], [getByID(triangle, 4242)])


    root = ET.Element('svg')
    root.set("version", "1.1")
    root.set("width", "1200px")
    root.set("height", "900px")
    root.set("version", "1.1")
    root.set("viewBox", f"{VIEWPORT_UL[0]} {VIEWPORT_UL[1]} {VIEWPORT_LR[0]-VIEWPORT_UL[0]} {VIEWPORT_LR[1]-VIEWPORT_UL[1]}")
    root.set("xmlns", "http://www.w3.org/2000/svg")

    style = ET.Element('style')
    style.text = "path { fill: #333333; stroke: none } .halfdart { fill: #ffff00 }"
    root.append(style)

    root.extend(getPaths(triangle))

    ET.indent(root)

    print(ET.tostring(root, encoding='unicode'))


