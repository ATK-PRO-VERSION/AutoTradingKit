from typing import List
from psygnal import evented
from dataclasses import dataclass
import numpy as np

@evented
@dataclass
class CandleDataConnect():
    x_data: np.ndarray
    y_data: List[np.ndarray]
    last_x_data: int
    last_y_data: np.ndarray
    
    def getdata(self):
        return self.x_data, self.y_data
    
    def setdata(self,xdata:list,ydata:List[list]):
        self.x_data = np.array([xdata])
        self.y_data = np.array([ydata])
        
    def updatedata(self,xdata:np.ndarray,ydata:List[np.ndarray]):
        self.x_data[-2:] = xdata[-2:]
        self.y_data[-2:] = ydata[-2:]
        
    def loaddata(self,xdata:list,ydata:List[list]):
        self.x_data = np.array([xdata])
        self.y_data = np.array([ydata])
    
