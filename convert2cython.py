import os
import traceback
import shutil

"pip install Cython"

def convert_to_cython(py_file):
    cy_file = ""
    if "init" not in py_file:
        with open(py_file, 'r',encoding= "utf-8") as f:
            py_code = f.read()
            cy_file = os.path.splitext(py_file)[0] + ".pyx"
            with open(cy_file, 'w',encoding="utf-8") as f:
                f.write(py_code)
    return cy_file

folders = [r"atklip\indicators\talipp",r"atklip\indicators\talipp\indicators",r"atklip\indicators\candle",
           r"atklip\graph_objects\chart_component",r"atklip\graph_objects\chart_component\base_items",
           r"atklip\graph_objects\chart_component\basic_indicators",
           r"atklip\exchanges",
           r"atklip\gui\qfluentwidgets\common", r"atklip\gui\qfluentwidgets\components\widgets", 
           r"atklip\gui\qfluentwidgets\components\date_time", r"atklip\gui\qfluentwidgets\components\container",
           r"atklip\gui\qfluentwidgets\components\navigation", r"atklip\gui\qfluentwidgets\components\settings",
           r"atklip\gui\qfluentwidgets\window", r"atklip\gui\components"]

indicators = [r"atklip\indicators\candle"]
pyqt_graph_folders = [r"atklip\graph_objects\pyqtgraph",
                      r"atklip\graph_objects\pyqtgraph\graphicsItems",
                      r"atklip\graph_objects\pyqtgraph\graphicsItems\ViewBox",
                      r"atklip\graph_objects\pyqtgraph\graphicsItems\PlotItem",
                      r"atklip\graph_objects\pyqtgraph\GraphicsScene",
                      r"atklip\graph_objects\pyqtgraph\canvas",
                      r"atklip\graph_objects\pyqtgraph\colors",
                      r"atklip\graph_objects\pyqtgraph\console",
                      r"atklip\graph_objects\pyqtgraph\dockarea",
                      r"atklip\graph_objects\pyqtgraph\imageview",
                      r"atklip\graph_objects\pyqtgraph\util",
                      r"atklip\graph_objects\pyqtgraph\widgets"
                      ]
def cythonize_one(folder, f):
    path_ = os.path.join(folder, f)
    if "__init__.py" not in path_:
        pyd_name = f.replace(".py",".pyd")
        pyx_path = convert_to_cython(path_)
        try:
            os.system(f'cythonize --build --inplace --3str --force --keep-going -j 40 {pyx_path}')
            _c_path = f'{str(pyx_path).replace(".pyx",".c")}'
            if os.path.exists(_c_path):
                os.remove(_c_path)
            _cpp_path = f'{str(_c_path).replace(".c",".cpp")}'
            if os.path.exists(_cpp_path):
                os.remove(_cpp_path)
            if os.path.exists(pyx_path):
                os.remove(pyx_path)
        except Exception as e:
            traceback.print_exception(e)

def convert_all(folders):
    list_pyx_path = []
    for folder in folders:
        
        pyd_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.pyd')]
        c_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.c')]
        cpp_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.cpp')]
        pyx_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.pyx')]

        html_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.html')]
        for html_file in html_files:
            os.remove(html_file)
        for pyd_file in pyd_files:
            os.remove(pyd_file)
        for c_file in c_files:
            os.remove(c_file)
        for c_file in cpp_files:
            os.remove(c_file)
        for pyx_file in pyx_files:
            if os.path.exists(pyx_file):
                os.remove(pyx_file)
        [cythonize_one(folder, f) for f in os.listdir(folder) if f.endswith('.py')]
        # for py_file in py_files:
        #     if "__init__.py" not in py_file:
        #         pyx_path = convert_to_cython(py_file)
        #         list_pyx_path.append(pyx_path)
        #         try:
        #             os.system(f'cythonize --build --inplace --3str --cplus --force --keep-going -j 40 --module-name {} {pyx_path}')
        #             _c_path = f'{str(pyx_path).replace(".pyx",".c")}'
        #             if os.path.exists(_c_path):
        #                 os.remove(_c_path)
        #             _cpp_path = f'{str(_c_path).replace(".c",".cpp")}'
        #             if os.path.exists(_cpp_path):
        #                 os.remove(_cpp_path)
        #             if os.path.exists(pyx_path):
        #                 os.remove(pyx_path)
        #         except Exception as e:
        #             traceback.print_exception(e)



def convert_one(path_:str=r"atklip\graph_objects\chart_component\viewchart.py"):
    pyx_path = convert_to_cython(path_)
    os.system(f'cythonize --build --inplace -3 --3str --force --keep-going -j 40 {path_}')


_list = [r"atklip\graph_objects\pyqtgraph\widgets",
         r"atklip\graph_objects\pyqtgraph\util",r"atklip\indicators\candle"]

# convert_all([r"atklip\indicators\talipp\indicators"])

# convert_all(pyqt_graph_folders)
# "atklip\graph_objects\pyqtgraph\GraphicsScene\GraphicsScene.py"
# "atklip\graph_objects\pyqtgraph\graphicsItems\PlotDataItem.py"
# "D:\AutoTradingKit\atklip\indicators\pandas_ta\utils"
convert_one(r"ta-lib-python-master/talib/_ta_lib.pyx")
# convert_all([r"D:\AutoTradingKit\atklip\indicators\pandas_ta\utils"])

# convert_one("graph_objects\pyqtgraph\WidgetGroup.py")

"""options:
  -h, --help            show this help message and exit
  -X NAME=VALUE,..., --directive NAME=VALUE,...
                        set a compiler directive
  -E NAME=VALUE,..., --compile-time-env NAME=VALUE,...
                        set a compile time environment variable
  -s NAME=VALUE, --option NAME=VALUE
                        set a cythonize option
  -2                    use Python 2 syntax mode by default
  -3                    use Python 3 syntax mode by default
  --3str                use Python 3 syntax mode by default
  -+, --cplus           Compile as C++ rather than C
  -a, --annotate        Produce a colorized HTML version of the source.
  --annotate-fullc      Produce a colorized HTML version of the source which includes entire generated C/C++-code.
  -x PATTERN, --exclude PATTERN
                        exclude certain file patterns from the compilation
  -b, --build           build extension modules using distutils/setuptools
  -i, --inplace         build extension modules in place using distutils/setuptools (implies -b)
  -j N, --parallel N    run builds in N parallel jobs (default: 12)
  -f, --force           force recompilation
  -q, --quiet           be less verbose during compilation
  --lenient             increase Python compatibility by ignoring some compile time errors
  -k, --keep-going      compile as much as possible, ignore compilation failures
  --no-docstrings       strip docstrings
  -M, --depfile         produce depfiles for the sources"""