import Tkinter as tk
import ttk
import time

class rtkWidget(object):
  Param={}
  bgcolor='#CCCCCC'
  def __init__(self,page,prop):
    page.widgets.append(self)
    self.prop=prop
    self.label=ttk.Label(page.frame,text=prop["label"],background=self.bgcolor,anchor="e")
    self.label.grid(row=len(page.widgets),column=1,sticky="nsew")
    self.timeout_=0
  def set_timeout(self,t):
    self.timeout_=time.time()+t    
  def on_timeout(self):
    return 0
  def update(self,t):
    if self.timeout_==0: return
    if t>self.timeout_:
      t1=self.timeout_
      self.on_timeout()
      if t1==self.timeout_: self.timeout_=0
    return
