import os

def convert_to_cython(py_file):
    cy_file = ""
    if "init" not in py_file:
        with open(py_file, 'r',encoding= "utf-8") as f:
            py_code = f.read()
            if "@njit(" in py_code:
                pyd_name = os.path.splitext(py_file)[0] + ".cp313-win_amd64.pyd"
                if os.path.exists(pyd_name):
                    print(pyd_name)
                    os.remove(pyd_name)
                    return None
            
            cy_file = os.path.splitext(py_file)[0] + ".pyx"
            with open(cy_file, 'w',encoding="utf-8") as f:
                f.write(py_code)
    return cy_file

def convert_one(path_:str=r"atklip\graph_objects\chart_component\viewchart.py"):
    pyx_path = convert_to_cython(path_)
    if not pyx_path:
        return
    os.system(f'cythonize --build --inplace -3 --3str --force --keep-going --no-docstrings {pyx_path}')
    
    _c_path = f'{str(pyx_path).replace(".pyx",".c")}'
    if os.path.exists(_c_path):
        os.remove(_c_path)
    _cpp_path = f'{str(_c_path).replace(".c",".cpp")}'
    if os.path.exists(_cpp_path):
        os.remove(_cpp_path)
    if os.path.exists(pyx_path):
        os.remove(pyx_path)
"atklip/graphics/chart_component"
"atklip/appmanager" "atklip/gui"
_list_dirs = ["atklip/controls"]
for dir in _list_dirs:
    for root, _, files in os.walk(dir):
        for file in files:
            src_path = os.path.join(root, file)
            # Bỏ qua thư mục __pycache__
            if "__pycache__" in src_path:
                continue
            
            elif "__init__" in src_path:
                continue
            
            elif "_ui" in src_path:
                continue
            
            # elif "controls" in src_path:
            #     continue
            elif "pyqtgraph" in src_path:
                continue
            elif "qfluentwidgets" in src_path:
                continue
            elif "app_api" in src_path:
                continue
            elif "app_utils" in src_path:
                continue
            elif "resource" in src_path:
                continue
            elif src_path.endswith(".ui"):
                continue
            elif not src_path.endswith(".py"):
                continue
            
            # if src_path.endswith(".pyd"):
            #     print("delete old",src_path)
            #     os.remove(src_path)
            
            if src_path.endswith(".py"):
                print(src_path)
                convert_one(src_path)