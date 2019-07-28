from .widget import rtkWidget
import collections

import Tkinter as tk
import ttk

import roslib
import rospy

class rtkText(rtkWidget):
  def __init__(self,page,prop):
    super(rtkText,self).__init__(page,prop)
    self.parse(prop["name"])
    self.io=tk.Entry(page.frame,width=16)
    self.io.grid(row=len(page.widgets),column=2,sticky="ns")
    self.io.insert(0,'---')
    self.value=''
    self.reflesh()
    self.io.bind('<Key-Return>',self.on_change)
    self.io.bind('<Key>',self.on_key)

  def parse(self,str):
    keys=str.split("/")
    self.lb=""
    self.rb=""
    for k in keys:
      if len(k)==0: continue
      self.lb=self.lb+"{'"+k+"':"
      self.rb=self.rb+'}'
  def merge(self,DCT,dct):
    for k,v in dct.iteritems():
      if (k in DCT and isinstance(DCT[k], dict) and isinstance(dct[k], collections.Mapping)):
        self.merge(DCT[k],dct[k])
      else:
        DCT[k]=dct[k]
  def set(self,value):
    self.io.delete(0,tk.END)
    self.io.insert(0,value)
    param=eval(self.lb+"'"+value+"'"+self.rb)
    self.merge(self.Param,param)
    self.value=value
    rospy.set_param(self.prop["name"],value)
  def on_change(self,event):
    self.set(self.io.get())
    self.io.config(foreground='#000000')
  def on_key(self,event):
    self.io.config(foreground='#FF0000')    
  def reflesh(self):
    try:
      value=rospy.get_param(self.prop["name"])
      if value!=self.value:
        self.set(value)
    except:
      rospy.logwarn("param "+self.prop["name"]+" not found")
    return
