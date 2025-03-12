import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor


global num_threads
num_threads = multiprocessing.cpu_count()

global ThreadPoolExecutor_global
ThreadPoolExecutor_global = ThreadPoolExecutor(max_workers=num_threads/2)

def convert_to_cython(py_file):
    cy_file = ""
    # if "init" not in py_file:
    with open(py_file, 'r',encoding= "utf-8") as f:
        py_code = f.read().encode("utf-8").decode("utf-8")
        # print("@njit(" in py_code)
        if "@njit(" in py_code or "@jit" in py_code:
            pyd_name = os.path.splitext(py_file)[0] + ".cp313-win_amd64.pyd"
            if os.path.exists(pyd_name):
                print(pyd_name)
                os.remove(pyd_name)
            return None
        # cy_file = os.path.splitext(py_file)[0] + ".pyx"
        # with open(cy_file, 'w',encoding="utf-8") as f:
        #     f.write(py_code)
    return py_file

def convert_one(path_:str=r"atklip\graph_objects\chart_component\viewchart.py"):
    pyx_path = convert_to_cython(path_)
    if not pyx_path:
        return
    try:
        os.system(f'cythonize --build --inplace -3 --3str --force --no-docstrings {pyx_path}') #
    except Exception as e:
        print(e)
    
    _c_path = f'{str(pyx_path).replace(".py",".c")}'
    if os.path.exists(_c_path):
        os.remove(_c_path)
    _cpp_path = f'{str(_c_path).replace(".c",".cpp")}'
    if os.path.exists(_cpp_path):
        os.remove(_cpp_path)
    # if os.path.exists(pyx_path):
    #     os.remove(pyx_path)

list_dirs = ["atklip/graphics/chart_component",
             "atklip/gui",
             "atklip/gui/components",
             "atklip/indicators",
             "atklip/controls",
             "atklip/app_api",
             "atklip/app_utils",
             "atklip/appmanager",
             "atklip/appdata",]

def convert_all(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            src_path = os.path.join(root, file)
            # Bỏ qua thư mục __pycache__
            if "__pycache__" in src_path:
                continue
            # elif "__init__" in src_path:
            #     continue
            # elif "_ui" in src_path:
            #     continue
            # elif "controls" in src_path:
            #     continue
            elif "pyqtgraph" in src_path:
                continue
            elif "qfluentwidgets" in src_path:
                continue
            # elif "app_api" in src_path:
            #     continue
            # elif "app_utils" in src_path:
            #     continue
            elif "resource" in src_path:
                continue
            elif src_path.endswith(".ui"):
                continue
            # elif not src_path.endswith(".py"):
            #     continue
            
            if src_path.endswith(".pyd"):
                print("delete old",src_path)
                os.remove(src_path)
                # continue
            
            elif src_path.endswith(".so"):
                print("delete old",src_path)
                os.remove(src_path)
                # continue

            elif src_path.endswith(".c"):
                print("delete old",src_path)
                os.remove(src_path)
                # continue

            elif src_path.endswith(".cpp"):
                print("delete old",src_path)
                os.remove(src_path)
                # continue

            elif src_path.endswith(".pyx"):
                print("delete old",src_path)
                os.remove(src_path)
                # continue

            
            if src_path.endswith(".py"):
                print(src_path)
                ThreadPoolExecutor_global.submit(convert_one,src_path)
                # convert_one(src_path)

convert_all(r"atklip")

# for folder in list_dirs:
#     convert_all(folder)

# convert_one(r"atklip\gui\views\fluentwindow.py")
# convert_one(r"atklip\graphics\chart_component\indicator_panel\indicator_panel_wg.py")
# convert_one(r"atklip\controls\pandas_ta\trend\trendflex.py")
# convert_one(r"atklip\controls\candle\smooth_candle.py")