import src.dartsandkites as dartsandkites
import src.robinson as robinson
import xml.etree.ElementTree as ET
from src.constants import VIEWPORT_UL, VIEWPORT_LR
from numpy import array

class DnkInterface():

    def __init__(self, rec_depth, border_thickness=0.001, border_color="#000000", dart_color="#ffaa00", kite_color="#0000aa"):
        
        self.svg = ET.Element('svg')
        self.svg.set("version", "1.1")
        self.svg.set("width", "1200px")
        self.svg.set("height", "900px")
        self.svg.set("version", "1.1")
        self.svg.set("viewBox", f"{VIEWPORT_UL[0]} {VIEWPORT_UL[1]} {VIEWPORT_LR[0]-VIEWPORT_UL[0]} {VIEWPORT_LR[1]-VIEWPORT_UL[1]}")
        self.svg.set("xmlns", "http://www.w3.org/2000/svg")

        self.styles = {
            "path": {
                "stroke": border_color,
                "stroke-width": str(border_thickness),
                "stroke-linejoin": "round"
            },
            ".dart": {
                "fill": dart_color
            },
            ".kite": {
                "fill": kite_color
            }
        }

        # assess border color
        self.updateBorder(border_thickness)
        

        self.paths = {}
        self.colors = {}

        self.style = self.getStyleElement()

        self.dnk = dartsandkites.DartsAndKites(robinson.P2(rec_depth))
        for tile in self.dnk.tiles:
            self.paths[tile.id] = tile.getPath()
            if tile.cls == "dart": self.colors[tile.id] = dart_color
            if tile.cls == "kite": self.colors[tile.id] = kite_color

    def updateBorder(self, width=-1, color=""):

        if width == -1: width = float(self.styles["path"]["stroke-width"])
        if color == "": color = self.styles["path"]["stroke"]

        self.use_fill_border = width < 0.0004
        if self.use_fill_border:
            self.styles["path"]["stroke-width"] = str(0.0003)
            self.styles[".dart"]["stroke"] = self.styles[".dart"]["fill"]
            self.styles[".kite"]["stroke"] = self.styles[".kite"]["fill"]
        else:
            self.styles["path"]["stroke-width"] = str(width)
            self.styles["path"]["stroke"] = color
            self.styles[".dart"]["stroke"] = self.styles["path"]["stroke"]
            self.styles[".kite"]["stroke"] = self.styles["path"]["stroke"]
        self.style = self.getStyleElement()

    def getStyleElement(self):
        elem = ET.Element('style')
        elem.text = ' '.join([selector+" { "+
                              "; ".join([attr+": "+val for attr, val in style.items()])
                              +" }" for selector, style in self.styles.items()])
        return elem

    def getSVGbytes(self):
        new_root = self.svg.__copy__()

        new_root.append(self.style)
        new_root.extend(self.paths.values())

        return ET.tostring(new_root)
    
    def paint(self, x, y, color) -> bool:
        click = array([x, y]) * (VIEWPORT_LR - VIEWPORT_UL) + VIEWPORT_UL
        id = self.dnk.getTileIDAtXY(click)
        if id == -1: return False
        self.paths[id].set('style', f"fill: {color};")
        self.colors[id] = color
        return True
    
    def getColor(self, x, y) -> str:
        click = array([x, y]) * (VIEWPORT_LR - VIEWPORT_UL) + VIEWPORT_UL
        id = self.dnk.getTileIDAtXY(click)
        if id == -1: return "#000000"
        return self.colors[id]

    

if __name__=="__main__":
    dnki = DnkInterface(1, 0.001, "red", "green", "blue")
    print(ET.tostring(dnki.getStyleElement(),encoding='unicode'))
