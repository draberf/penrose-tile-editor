import src.robinson as robinson
import numpy as np
import xml.etree.ElementTree as ET
from src.utils_geometry import ccw, pointInTriangle
from src.constants import VIEWPORT_UL, VIEWPORT_LR


def tileFactory(type: str, triangle1: robinson.Robinson, triangle2: robinson.Robinson) -> 'Tile':
    
    
    
    if type == "halfkite":
        return Kite(triangle1.a, triangle1.b, triangle1.c, triangle2.b)
    if type == "halfdart":
        return Dart(triangle1.a, triangle1.b, triangle2.a, triangle1.c)
    
    return None

class Tile:

    ID = 0

    def __init__(self, a: [np.float_], b: [np.float_], c: [np.float_], d: [np.float_]):
        self.a, self.b, self.c, self.d = a, b, c, d
        self.references = []
        self.cls = ""
        self.fill = "black"
        self.id = Tile.ID
        Tile.ID += 1

    def isIn(self, x: [np.float_]) -> bool:
        return False
    
    def getPath(self) -> ET.Element:
        elem = ET.Element('path')
        elem.set('d', f"M {self.a[0]} {self.a[1]} L {self.b[0]} {self.b[1]} {self.c[0]} {self.c[1]} {self.d[0]} {self.d[1]} z")
        elem.set('class', f"{self.cls}")
        elem.set('id', f'{self.id}')

        return elem

class Dart(Tile):
    # A < B << C >> D > A
    # axis A >>>> C
    def __init__(self, a: [np.float_], b: [np.float_], c: [np.float_], d: [np.float_]):
        super().__init__(a, b, c, d)
        self.cls = "dart"
        self.fill = "cyan"


    def isIn(self, x: [np.float_]) -> bool:
            return pointInTriangle(self.b, self.c, self.d, self,x) and not pointInTriangle(self.d, self.b, self.a, self.x)

class Kite(Tile):
    # A > B >> C << D < A
    # axis C >>> A
    def __init__(self, a: [np.float_], b: [np.float_], c: [np.float_], d: [np.float_]):
        super().__init__(a, b, c, d)
        self.cls = "kite"
        self.fill = "gray"
    
    def isIn(self, x: [np.float_]) -> bool:
        return pointInTriangle(self.a, self.b, self.c, self,x) or pointInTriangle(self.c, self.d, self.a)


class DartsAndKites:

    def __init__(self, p2: robinson.P2):
        self.tiles = []
        self.references = {}
        self.p2 = p2

        for triangle in p2.triangle.getAllLeaves():
            # avoid duplication: only process a tile when finding the ccw half
            if triangle.getMirror() and not ccw(triangle.a, triangle.b, triangle.c): continue 


            opposite = triangle.getMirror()
            if not opposite:
                opposite = robinson.Robinson(triangle.b, triangle.c, triangle.a)
                opposite.id = -1
            new_tile = tileFactory(triangle.cls, triangle, opposite)
            new_tile.references = [triangle.id, opposite.id]
            self.references[triangle.id] = new_tile
            if opposite.id != -1: self.references[str(opposite.id)] = new_tile

            self.tiles.append(new_tile)

    def getSVG(self) -> ET.Element:
        root = ET.Element('svg')
        root.set("version", "1.1")
        root.set("width", "1200px")
        root.set("height", "900px")
        root.set("version", "1.1")
        root.set("viewBox", f"{VIEWPORT_UL[0]} {VIEWPORT_UL[1]} {VIEWPORT_LR[0]-VIEWPORT_UL[0]} {VIEWPORT_LR[1]-VIEWPORT_UL[1]}")
        root.set("xmlns", "http://www.w3.org/2000/svg")

        style = ET.Element('style')
        style.text = "path { stroke: black; stroke-width: 0.001 }"
        root.append(style)

        root.extend([tile.getPath() for tile in self.tiles])

        return root
    
    def getTileIDAtXY(self, x) -> int:
        id = robinson.searchSmallestAtPoint(self.p2.triangle, x)
        if id == -1: return -1
        return self.references[id].id

if __name__=="__main__":

    p2 = robinson.P2(11)

    dnk = DartsAndKites(p2)

    click = np.array([0.1,0.5])
    id = robinson.searchSmallestAtPoint(p2.triangle, click)
    #dnk.references[id].fill = "red"


    svg = dnk.getSVG()



    with open('output_dnk.svg', 'wb+') as f:
        f.write(ET.tostring(svg))
