import xml.etree.ElementTree as ET
import os
def change_svg_color(value, new_color):
    
    path = f'E:/att-algo-trading-tools/gui/qfluentwidgets/_rc/images/icons/{value}.svg'
    new_path = f'E:/att-algo-trading-tools/gui/qfluentwidgets/_rc/images/icons/{value}_{new_color}.svg' 
    # Check if any element has a 'fill' attribute
    #print("path", path)
    tree = ET.parse(path)
    root = tree.getroot()
    has_fill = False
    for element in root.iter():
        if 'fill' in element.attrib:
            has_fill = True
            break

    # If 'fill' attribute exists, change its color
    if has_fill:
        for element in root.iter():
            if 'fill' in element.attrib:
                element.attrib['fill'] = new_color
    else:
        # If 'fill' attribute doesn't exist, add it to all relevant elements
        for element in root.iter():
            if element.tag.endswith('path') or element.tag.endswith('rect') \
                or element.tag.endswith('circle') or element.tag.endswith('ellipse') or element.tag.endswith('line') \
               or element.tag.endswith('polyline') or element.tag.endswith('polygon'):
                element.attrib['fill'] = new_color
    # Save the modified SVG to a new file
    tree.write(new_path)
    return new_path

def change_svg_color(value:str, new_color):
    path = f'atklip/gui/qfluentwidgets/_rc/images/icons/{value}_white.svg'
    new_path = f'atklip/gui/qfluentwidgets/_rc/images/icons/{value.lower()}_tradingview.svg'
    if os.path.exists(new_path):
        return new_path
    file = open(path,"r")
    text = file.read()
    file.close()
    file = open(new_path,'w')
    new_text = text.replace("rgb(255,255,255)",new_color).replace("rgb(0,0,0)",new_color).replace("white",new_color).replace("rgb(247,245,245)",new_color) 
    file.write(new_text)
    file.close()
    return new_path


def change_svg(value:str):
    path = f'atklip/gui/qfluentwidgets/_rc/images/icons/{value}'
    new_path = f'atklip/gui/qfluentwidgets/_rc/images/icons/{value.lower()}'
    # if os.path.exists(new_path):
    #     return new_path
    file = open(path,"r",encoding="utf-8")
    text = file.read()
    file.close()
    os.remove(path)
    file = open(new_path,'w',encoding="utf-8")
    #new_text = text.replace("rgb(255,255,255)",new_color).replace("rgb(0,0,0)",new_color).replace("white",new_color).replace("rgb(247,245,245)",new_color) 
    file.write(text)
    file.close()
    
    return new_path

list_icon = os.listdir(f"atklip/gui/qfluentwidgets/_rc/images/icons")

# {value.lower()}_white.svg
for i in list_icon:
    # if i.__contains__('.svg'):
    #     print(i)
    #     change_svg(i)
    if i.__contains__('_white.svg'):
        i = i[:-10]
        print(i)
        change_svg_color(i,"#0055ff")