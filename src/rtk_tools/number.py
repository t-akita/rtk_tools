from .text import rtkText
from . import dictlib

import tkinter as tk
import tkinter.ttk as ttk

import roslib
import rospy

class rtkNumber(rtkText):
  def on_init(self):
    super(rtkText,self).on_init()
    dictlib.merge(self.prop,{"format":""})

  def __init__(self,page,prop):
    super(rtkNumber,self).__init__(page,prop)
    self.io.config(justify="right")
    self.vect=None
    if "index" not in self.prop: self.prop["index"]=0

  def set(self,value):
    if type(value) is str:
      super(rtkNumber,self).set(value)
      return
    self.io.delete(0,tk.END)
    if len(self.prop["format"])>0:
      fmt="{:"+self.prop["format"]+"}"
      self.io.insert(0,fmt.format(value))
    else:
      self.io.insert(0,str(value))
    if self.vect is None:
      param=eval(self.lb+str(value)+self.rb)
      rospy.set_param(self.prop["name"],value)
    else:
      self.vect[self.prop["index"]]=value
      param=eval(self.lb+str(self.vect)+self.rb)
      rospy.set_param(self.prop["name"],self.vect)
    dictlib.merge(self.Param,param)
    self.value=value

  def on_change(self,event):
    try:
      sval=self.io.get()
      if "." in sval:
        nval=float(sval)
      else:
        nval=int(sval)
      self.set(nval)
      self.io.config(foreground='#000000')
    except:
      super(rtkNumber,self).on_change(event)

  def on_timeout(self):
    try:
      value=rospy.get_param(self.prop["name"])
      if type(value) is list:
        self.vect=value
        value=self.vect[self.prop["index"]]
      if type(value) is str:
        if "." in value:
          value=float(value)
        else:
          value=int(value)
      if value!=self.value:
        self.set(value)
    except:
      rospy.logwarn("param "+self.prop["name"]+" not found or wrong number")
    self.set_timeout(self.interval)
    return
