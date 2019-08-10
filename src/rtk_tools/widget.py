import Tkinter as tk
import ttk
import time

class rtkWidget(object):
  Param={}
  bgcolor='#CCCCCC'
  def __init__(self,page,prop):
    page.widgets.append(self)
    try:
      self.merge(self.prop,prop)
    except:
      self.prop=prop
    self.label=ttk.Label(page.frame,text=prop["label"],background=self.bgcolor,anchor="e")
    self.label.grid(row=len(page.widgets),column=1,sticky="nsew")
    self.timeout_=0
  def merge(self,DCT,dct):
    for k,v in dct.iteritems():
      if (k in DCT and isinstance(DCT[k], dict) and isinstance(dct[k], dict)):
        self.merge(DCT[k],dct[k])
      else:
        DCT[k]=dct[k]
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
