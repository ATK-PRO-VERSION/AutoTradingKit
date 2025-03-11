
import os
import traceback
from Cython.Build import cythonize
from setuptools import setup
from Cython.Build import cythonize
import shutil
import mypy
def convert_to_cython(py_file):
    cy_file = ""
    with open(py_file, 'r',encoding= "utf-8") as f:
        py_code = f.read()
        cy_file = os.path.splitext(py_file)[0] + ".pyx"
        with open(cy_file, 'w',encoding="utf-8") as f:
            f.write(py_code)
    return cy_file

folders = [r"indicators\talipp",r"indicators\talipp\indicators",r"indicators\candle",
           r"graph_objects\chart_component",r"graph_objects\chart_component\base_items",
           r"graph_objects\chart_component\basic_indicators",
           r"exchanges",
           r"gui\qfluentwidgets\common", r"gui\qfluentwidgets\components\widgets", 
           r"gui\qfluentwidgets\components\date_time", r"gui\qfluentwidgets\components\container",
           r"gui\qfluentwidgets\components\navigation", r"gui\qfluentwidgets\components\settings",
           r"gui\qfluentwidgets\window", r"gui\components"]

list_pyx_path = []
for folder in folders:
    py_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.py')]
    for py_file in py_files:
        if "__init__.py" not in py_file:
            try:
                os.system(f'stubgen {py_file} --ignore-errors --no-import --no-analysis  --parse-only --include-private')
            except Exception as e:
                traceback.print_exception(e)
