import asyncio
import datetime
import json
import os
import re
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import requests
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Slot, Qt, Signal, QEvent, QSize, QPointF, QKeyCombination, QThreadPool
from PySide6.QtGui import QMovie, QKeyEvent, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton, QFrame,QMessageBox
from pyqtgraph import InfiniteLine, mkPen, mkColor, PlotDataItem,mkBrush

from atklip.graphics.chart_component.base_items.rs_object import RSObject


class Objects(object):
    def __init__(self,time:int,pos:float,high:float,low:float,open_:float,close:float,label:str="none", id=None) -> object:
        self.pos = pos
        self.time = time
        self.high = high
        self.low = low
        self.open = open_
        self.close = close
        self.label = label
        self.id = id
    
    def get_paras_long(self):
        curr_time, curr_low, curr_high,curr_open, curr_close = self.time,self.low,self.high,self.open,self.close
        return curr_time, curr_low, curr_high,curr_open, curr_close
    def get_paras_short(self):
        curr_time, curr_low, curr_high,curr_open, curr_close = self.time,self.low,self.high,self.open,self.close
        return curr_time, curr_low, curr_high,curr_open, curr_close
    def setPos(self,time,pos,high:float,low:float,open_:float,close:float):
        self.pos = pos
        self.time = time
        self.high = high
        self.low = low
        self.open = open_
        self.close = close
    
    def getpos(self):
        return self.pos
    def gettime(self):
        return self.time
    def getlabel(self):
        return self.label
    
class values():
    def __init__(self) -> None:
        
        self.v0up_line = Objects(0,0,0,0,0,0,"VL_0up")
        self.v0dw_line = Objects(0,0,0,0,0,0,"VL_0dw")
        
        
        self.pre_vl1dw = 0
        self.pre_vl1up = 0
        
        self.vl0up = Objects(0,0,0,0,0,0,"Up_VL_0.0")
        self.vl1up = Objects(0,0,0,0,0,0,"Up_VL_1.0")
        self.vl2up = Objects(0,0,0,0,0,0,"Up_VL_2.0")
        
        self.vl0dw = Objects(0,0,0,0,0,0,"Dw_VL_0.0")
        self.vl1dw = Objects(0,0,0,0,0,0,"Dw_VL_1.0")
        self.vl2dw = Objects(0,0,0,0,0,0,"Dw_VL_2.0")
       
    def change_version(self,vl):
        #vl0up_txt = self.vl0up.label().toPlainText()
        vl_txt = vl.label
        
        version = re.findall(r'\d+', vl_txt)

        if float(vl.pos) == 0:
            return
        
        #version12 = re.findall(r'\d+', vl_txt)
        version = str(int(version[1])+1)
        if "Up_VL_0" in vl_txt:
            name = f"Up_VL_0.{version}"
            self.vl0up.label = name
        if "Up_VL_1" in vl_txt:
            name = f"Up_VL_1.{version}"
            self.vl1up.label = name
        if "Up_VL_2" in vl_txt:
            name = f"Up_VL_2.{version}"
            self.vl2up.label = name
        if "Dw_VL_0" in vl_txt:
            name = f"Dw_VL_0.{version}"
            self.vl0dw.label = name
        if "Dw_VL_1" in vl_txt:
            name = f"Dw_VL_1.{version}"
            self.vl1dw.label = name
        if "Dw_VL_2" in vl_txt:
            name = f"Dw_VL_2.{version}"
            self.vl2dw.label = name

class cancu():
    def __init__(self) -> None:
        self.list_cancu_long = []
        self.list_cancu_short = []

        self.list_cancu_long_main_trend = []
        self.list_cancu_short_main_trend = []

    
    def change_version(self,vl):
        #vl0up_txt = self.vl0up.label().toPlainText()
        vl_txt = vl.label
        
        version = re.findall(r'\d+', vl_txt)

        if float(vl.pos) == 0:
            return
        
        #version12 = re.findall(r'\d+', vl_txt)
        version = str(int(version[1])+1)
        if "Up_VL_0" in vl_txt:
            name = f"Up_VL_0.{version}"
            self.vl0up.label = name
        if "Up_VL_1" in vl_txt:
            name = f"Up_VL_1.{version}"
            self.vl1up.label = name
        if "Up_VL_2" in vl_txt:
            name = f"Up_VL_2.{version}"
            self.vl2up.label = name
        if "Dw_VL_0" in vl_txt:
            name = f"Dw_VL_0.{version}"
            self.vl0dw.label = name
        if "Dw_VL_1" in vl_txt:
            name = f"Dw_VL_1.{version}"
            self.vl1dw.label = name
        if "Dw_VL_2" in vl_txt:
            name = f"Dw_VL_2.{version}"
            self.vl2dw.label = name
    def analys_x_step(self,vl):
        #vl0up_txt = self.vl0up.label().toPlainText()
        vl_txt = vl.label
        
        version = re.findall(r'\d+', vl_txt)

        if float(vl.pos) == 0:
            return
        
        #version12 = re.findall(r'\d+', vl_txt)
        version = str(int(version[1])+1)
        if "Up_VL_0" in vl_txt:
            name = f"Up_VL_0.{version}"
            self.vl0up.label = name
        if "Up_VL_1" in vl_txt:
            name = f"Up_VL_1.{version}"
            self.vl1up.label = name
        if "Up_VL_2" in vl_txt:
            name = f"Up_VL_2.{version}"
            self.vl2up.label = name
        if "Dw_VL_0" in vl_txt:
            name = f"Dw_VL_0.{version}"
            self.vl0dw.label = name
        if "Dw_VL_1" in vl_txt:
            name = f"Dw_VL_1.{version}"
            self.vl1dw.label = name
        if "Dw_VL_2" in vl_txt:
            name = f"Dw_VL_2.{version}"
            self.vl2dw.label = name


class Support_Resistance():
    def __init__(self):
        self.vls = values()
        self.cancu = cancu()
        self.listheadbases = []

        
    def add_cancu_long(self,curr_time, curr_low, curr_high,curr_open, curr_close,cancu_type="real"):
        """add_cancu_long _summary_
        Thêm một hỗ trợ vào danh sách lưu các đường hỗ trợ
        _extended_summary_

        Args:
            curr_time (_type_): _description_
            curr_low (_type_): _description_
            curr_high (_type_): _description_
            curr_open (_type_): _description_
            curr_close (_type_): _description_
            cancu_type (str, optional): _description_. Defaults to "real".
        """
        vrange = self.vb.viewRange()
        low = min(curr_open, curr_close)
        low_longwick = (low- curr_low)/3
        low_normal = low- curr_low
        x1 = vrange[0][1]
        line = RSObject((curr_time, curr_low),(x1,low_normal),pen="green")
            #line.setPen(color="green")
        self.addItem(line)
        line_id = self.object_id.add(line)
        line.id = line_id
        line.type_rs = "long"
        self.cancu.list_cancu_long.append(line_id)
        
    def add_cancu_short(self,curr_time, curr_low, curr_high,curr_open, curr_close,cancu_type="real"):
        """add_cancu_short _summary_
        Thêm một kháng cự vào danh sách lưu các đường kháng cự
        _extended_summary_

        Args:
            curr_time (_type_): _description_
            curr_low (_type_): _description_
            curr_high (_type_): _description_
            curr_open (_type_): _description_
            curr_close (_type_): _description_
            cancu_type (str, optional): _description_. Defaults to "real".
        """
        vrange = self.vb.viewRange()
        high = max(curr_open, curr_close)
        high_longwick = (curr_high- high)/3
        high_normal = curr_high- high
        x1 = vrange[0][1]
        line = RSObject((curr_time, curr_high-high_normal),(x1,high_normal),pen="red")
        self.addItem(line)
        line_id = self.object_id.add(line)
        line.id = line_id
        line.type_rs = "short"
        self.cancu.list_cancu_short.append(line_id)


    def percent(self,start, stop):
        """percent _summary_
        Tính toán phần trăm chênh lệch giá từ điểm start đến stop
        _extended_summary_

        Args:
            start (_type_): value bắt đầu
            stop (_type_): value kết thúc

        Returns:
            _type_: _description_
        """
        if start != 0:
            percent = float(((float(start) - float(stop)) / float(start))) * 100
            if percent > 0:
                return percent
            else:
                return abs(percent)
        return None


    def set_vl0line_up_pos(self,time,pos):
        #self.vls.v0up_line.setPos(time,pos)
        self.listheadbases.append({
        "time": int(time),
        "price": pos,
        "type": "under"
        })

    def set_vl0line_dw_pos(self,time,pos):
        #self.vls.v0dw_line.setPos(time,pos)
        self.listheadbases.append({
        "time": int(time),
        "price": pos,
        "type": "above"
        })
    
    def backtest_candle(self, event=None,btn_name=None):
        """
        Khi chạy 1 nến mới thì chạy vào hàm này để kiểm tra các điều kiện của đường hỗ trợ, kháng cự, và chart parten
        các logic nằm cả ở đây
        """
        self.percent_filter = 1
        self.percent_filter_on = 3
        

        if self.timedata[-1] <= self.timedata_[-1]:

            pre_time = self.timedata[-2]
            pre_data = self.data[-2]
            
            current_time = self.timedata[-1]
            candle_data = self.data[-1]

            pre_candle = {'time': pre_time, 'open': pre_data[0], 'high':  pre_data[3], 'low':  pre_data[2], 'close':  pre_data[1]}
            candle = {'time': current_time, 'open': candle_data[0], 'high':  candle_data[3], 'low':  candle_data[2], 'close':  candle_data[1]}
            
            cr_high,cr_low,cr_open,cr_close = candle["high"], candle["low"], candle["open"], candle["close"]
            

            '''vl0,vl2 thì bị dời khi râu nến chọt qua, bị dời khi thân nến chọt qua'''
            if cr_low <= self.vls.vl0up.getpos():
                self.vls.vl0up.setPos(candle["time"], cr_low,cr_high,cr_low,cr_open,cr_close)
                self.vls.vl1up.setPos(0,0,0,0,0,0)
                self.vls.vl2up.setPos(0,0,0,0,0,0)
                self.set_vl0line_up_pos(candle["time"],cr_low)
                self.vls.pre_vl1up = cr_low
            else:
                '''Từ vl0 thỏa quy tắt đóng nến thì tìm vl1, vl1 thỏa quy tắt đóng nến thì tìm vl2'''
                if self.vls.vl1up.getpos()==0:
                    if  (cr_open <= pre_candle["high"]  <=  cr_close) or (cr_close <= pre_candle["high"]  <=  cr_open):
                        self.vls.vl1up.setPos(candle["time"], cr_high,cr_high,cr_low,cr_open,cr_close)
                        if self.percent(self.vls.vl0up.getpos(),self.vls.vl1up.getpos()) >= self.percent_filter:
                            curr_time_, curr_low_, curr_high_,curr_open_, curr_close_ = self.vls.vl0up.get_paras_long()
                            self.add_cancu_long(curr_time_, curr_low_, curr_high_,curr_open_, curr_close_,"real")

                
                elif self.vls.vl2up.getpos()==0:
                    if cr_close >= self.vls.vl1up.getpos():
                        self.vls.vl1up.setPos(candle["time"], cr_high,cr_high,cr_low,cr_open,cr_close)
                        #self.vls.change_version(self.vls.vl1up)
                        '''vl0,vl2 thì bị dời khi râu nến chọt qua, bị dời khi thân nến chọt qua'''
                        self.vls.vl2up.setPos(0,0,0,0,0,0)
                        
                        "update value vl2up o day"
                        # if self.vls.vl1up.getpos() >  self.vls.pre_vl1up:
                        #     self.vls.pre_vl1up = self.vls.vl1up.getpos()
                        
                    elif  (cr_close <= pre_candle["low"]  <=  cr_open) or (cr_open <= pre_candle["low"]  <=  cr_close):
                        
                        """Khi thỏa quy tắt đống nến tìm điểm VL2U thì so sánh vl1u < vl0d thì lấy vl0d là vl1u"""
                        if (self.vls.vl1up.getpos() < self.vls.vl0dw.getpos()) and (self.vls.vl1up.gettime() < self.vls.vl0dw.gettime() ):
                            self.vls.vl1up.setPos(self.vls.vl0dw.gettime(),self.vls.vl0dw.getpos(),cr_high,cr_low,cr_open,cr_close)

                        self.vls.vl2up.setPos(candle["time"], cr_low,cr_high,cr_low,cr_open,cr_close)
                        
                        if self.vls.vl1up.getpos() >  self.vls.pre_vl1up:
                            self.vls.pre_vl1up = self.vls.vl1up.getpos()
                else: 
                    if cr_low <= self.vls.vl2up.getpos() and cr_high < self.vls.vl1up.getpos():
                        """Khi thỏa quy tắt đống nến tìm điểm VL2U thì so sánh vl1u < vl0d thì lấy vl0d là vl1u"""
                        # if self.vls.vl1up.getpos() < self.vls.vl0dw.getpos() and self.vls.vl1up.gettime() < self.vls.vl0dw.gettime() :
                        #     self.vls.vl1up.setPos(self.vls.vl0dw.gettime(),self.vls.vl0dw.getpos())
                        #     # if self.vls.vl1up.getpos() >  self.vls.pre_vl1up:
                            #     self.vls.pre_vl1up = self.vls.vl1up.getpos()
                            
                        # elif self.vls.vl1up.getpos() > self.vls.vl0dw.getpos():
                        #     self.vls.vl0dw.setPos(self.vls.vl1up.gettime(),self.vls.vl1up.getpos())
                        
                        self.vls.vl2up.setPos(candle["time"], cr_low,cr_high,cr_low,cr_open,cr_close)
                        #self.vls.change_version(self.vls.vl2up)

                    elif (cr_high >= (self.vls.vl1up.getpos() + self.vls.vl2up.getpos())/2  and (self.percent(self.vls.vl2up.getpos(),cr_high) >= self.percent_filter/2)):  # can cu xac dinh khi high > vl1
                    
                        
                        if len(self.cancu.list_cancu_long) == 0:
                            center_value = (self.vls.vl0up.getpos()+self.vls.vl1up.getpos())/2
                        else:
                            
                            #list_cancu_long = [self.object_id.get(id_cancu).pos().y() for id_cancu in self.cancu.list_cancu_long]
                            list_cancu_long = []
                            for id_cancu in self.cancu.list_cancu_long:
                                rs = self.object_id.get(id_cancu)
                                if isinstance(rs,RSObject):
                                    list_cancu_long.append(rs.pos().y())
                            
                            max_long_value = max(list_cancu_long)
                            #last_long = self.object_id.get(self.cancu.list_cancu_long[-1])  
                            center_value = (max_long_value+self.vls.pre_vl1up)/2
                            
                        curr_time_, curr_low_, curr_high_,curr_open_, curr_close_ = self.vls.vl2up.get_paras_long()
                        if self.percent(self.vls.vl1up.getpos(),self.vls.vl2up.getpos()) >= self.percent_filter:
                            if self.vls.vl2up.getpos() > center_value:
                                self.add_cancu_long(curr_time_, curr_low_, curr_high_,curr_open_, curr_close_,"real")
                                #self.add_cancu_long(self.vls.vl2up.gettime(),self.vls.vl2up.getpos(),"real")
                                # if self.vls.vl1up.getpos() >  self.vls.pre_vl1up:
                                #     self.vls.pre_vl1up = self.vls.vl1up.getpos()
                            else:
                                self.add_cancu_long(curr_time_, curr_low_, curr_high_,curr_open_, curr_close_,"real")
                                # if self.vls.vl1up.getpos() >  self.vls.pre_vl1up:
                                #     self.vls.pre_vl1up = self.vls.vl1up.getpos()
                        "TESTING"
                        #self.vls.vl0up.setPos(candle["time"], cr_low,cr_high,cr_low,cr_open,cr_close)
                        self.vls.vl0up.setPos(curr_time_, curr_low_, curr_high_,curr_low_,curr_open_, curr_close_)
                        self.vls.vl1up.setPos(0,0,0,0,0,0)
                        self.vls.vl2up.setPos(0,0,0,0,0,0)
                        self.set_vl0line_up_pos(candle["time"],cr_low)
                        self.vls.pre_vl1up = cr_low
                        "END"
                            #self.vls.vl1up.setPos(candle["time"], cr_high,cr_high,cr_low,cr_open,cr_close)
                            # '''vl0,vl2 thì bị dời khi râu nến chọt qua, bị dời khi thân nến chọt qua'''
                            # self.vls.vl2up.setPos(0,0,0,0,0,0)
                    
            if cr_high >= self.vls.vl0dw.getpos():
                self.vls.vl0dw.setPos(candle["time"], cr_high,cr_high,cr_low,cr_open,cr_close)
                #self.vls.change_version(self.vls.vl0dw)
                self.vls.vl1dw.setPos(0,0,0,0,0,0)
                self.vls.vl2dw.setPos(0,0,0,0,0,0)
                self.set_vl0line_dw_pos(candle["time"],cr_high)
                
                #self.vls.pre_vl1up = 0
                self.vls.pre_vl1dw = cr_high
            else:
                if self.vls.vl1dw.getpos()==0:
                    if  (cr_close <= pre_candle["low"]  <=  cr_open) or (cr_open <= pre_candle["low"]  <=  cr_close):
                    
                        self.vls.vl1dw.setPos(candle["time"], cr_low,cr_high,cr_low,cr_open,cr_close)
                        if self.percent(self.vls.vl0dw.getpos(),self.vls.vl1dw.getpos()) >= self.percent_filter:
                            curr_time_,  curr_low_, curr_high_,curr_open_, curr_close_ = self.vls.vl0dw.get_paras_short()
                            self.add_cancu_short(curr_time_,  curr_low_, curr_high_,curr_open_, curr_close_, "real")
                        #self.vls.change_version(self.vls.vl1dw)
                        # if self.vls.vl1dw.getpos() < self.vls.pre_vl1dw:
                        #     self.vls.pre_vl1dw = self.vls.vl1dw.getpos()

                elif self.vls.vl2dw.getpos()==0:

                    if cr_close <= self.vls.vl1dw.getpos():
                        
                        self.vls.vl1dw.setPos(candle["time"], cr_low,cr_high,cr_low,cr_open,cr_close)
                        #self.vls.change_version(self.vls.vl1dw)
                        self.vls.vl2dw.setPos(0,0,0,0,0,0)
                        "update value vl2up o day"
                        # if self.vls.vl1dw.getpos() < self.vls.pre_vl1dw:
                        #     self.vls.pre_vl1dw = self.vls.vl1dw.getpos()

                    elif  (cr_open <= pre_candle["high"]  <=  cr_close) or (cr_close <= pre_candle["high"]  <=  cr_open):
                        
                        """Khi thỏa quy tắt đống nến tìm điểm VL2D thì só sánh vl1d > vl0u thì lấy vl1d là vl0u"""
                        if self.vls.vl1dw.getpos() > self.vls.vl0up.getpos() and self.vls.vl1dw.gettime() < self.vls.vl0up.gettime():
                            self.vls.vl1dw.setPos(self.vls.vl0up.gettime(),self.vls.vl0up.getpos(),cr_high,cr_low,cr_open,cr_close)
                            

                        self.vls.vl2dw.setPos(candle["time"], cr_high,cr_high,cr_low,cr_open,cr_close)
                        #self.vls.change_version(self.vls.vl2dw)
                        if self.vls.vl1dw.getpos() < self.vls.pre_vl1dw:
                            self.vls.pre_vl1dw = self.vls.vl1dw.getpos()

                else:
                    
                    if cr_high >= self.vls.vl2dw.getpos():

                            # """Khi thỏa quy tắt đống nến tìm điểm VL2D thì só sánh vl1d > vl0u thì lấy vl1d là vl0u"""
                            # if self.vls.vl1dw.getpos() > self.vls.vl0up.getpos() and self.vls.vl1dw.gettime() < self.vls.vl0up.gettime():
                            #     self.vls.vl1dw.setPos(self.vls.vl0up.gettime(),self.vls.vl0up.getpos())
                                # if self.vls.vl1dw.getpos() < self.vls.pre_vl1dw:
                                #     self.vls.pre_vl1dw = self.vls.vl1dw.getpos()
                            self.vls.vl2dw.setPos(candle["time"], cr_high,cr_high,cr_low,cr_open,cr_close)
                            #self.vls.change_version(self.vls.vl2dw)
                            
                    elif (cr_low <= (self.vls.vl1dw.getpos() + self.vls.vl2dw.getpos())/2 and (self.percent(self.vls.vl2dw.getpos(),cr_low) >= self.percent_filter/2)):
                        
                        if len(self.cancu.list_cancu_short) == 0:
                            center_value = (self.vls.vl0dw.getpos()+self.vls.vl1dw.getpos())/2
                            
                        else:
                            #list_cancu_short = [self.object_id.get(id_cancu).pos().y() for id_cancu in self.cancu.list_cancu_short]
                            list_cancu_short = []
                            for id_cancu in self.cancu.list_cancu_short:
                                rs = self.object_id.get(id_cancu)
                                if isinstance(rs,RSObject):
                                    list_cancu_short.append(rs.pos().y())
                            min_short_value = min(list_cancu_short)
                            #last_short = self.object_id.get(self.cancu.list_cancu_short[-1]) 
                            center_value = (min_short_value+self.vls.pre_vl1dw)/2
                            
                            print(len(self.cancu.list_cancu_short), min_short_value,self.vls.pre_vl1dw, center_value, self.vls.vl2dw.getpos())
                        
                        curr_time_,  curr_low_, curr_high_,curr_open_, curr_close_ = self.vls.vl2dw.get_paras_short()
                        if self.percent(self.vls.vl1dw.getpos(),self.vls.vl2dw.getpos()) >= self.percent_filter:
                            if self.vls.vl2dw.getpos()< center_value:
                                self.add_cancu_short(curr_time_,  curr_low_, curr_high_,curr_open_, curr_close_, "real")
                                # if self.vls.vl1dw.getpos() < self.vls.pre_vl1dw:
                                #     self.vls.pre_vl1dw = self.vls.vl1dw.getpos()
                            else:
                                self.add_cancu_short(curr_time_,  curr_low_, curr_high_,curr_open_, curr_close_, "real")
                                # if self.vls.vl1dw.getpos() < self.vls.pre_vl1dw:
                                #     self.vls.pre_vl1dw = self.vls.vl1dw.getpos()
                        "TESTING"
                        #self.vls.vl0dw.setPos(candle["time"], cr_high,cr_high,cr_low,cr_open,cr_close)
                        self.vls.vl0dw.setPos(curr_time_, curr_high_,curr_high_,curr_low_,curr_open_, curr_close_)
                        self.vls.vl1dw.setPos(0,0,0,0,0,0)
                        self.vls.vl2dw.setPos(0,0,0,0,0,0)
                        self.set_vl0line_dw_pos(candle["time"],cr_high)
                        self.vls.pre_vl1dw = cr_high
                        "END"
                        #self.vls.vl1dw.setPos(candle["time"], cr_low,cr_high,cr_low,cr_open,cr_close)
                        # self.vls.vl2dw.setPos(0,0,0,0,0,0)