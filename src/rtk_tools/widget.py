import tkinter as tk
from tkinter import ttk
import time
from . import dictlib

class rtkWidget(object):
  Origin={}
  Param={}
  Config={
    "width":(0,10),
    "font":{
      "family":"System",
      "size":10
    },
    "color":{
      "background": "#00FF00",
      "title": ("#FFFFFF","#555555"),
      "label": ("#000000","#CCCCCC")
    }
  }
  def on_init(self):
    try:
      n=len(self.prop.keys())
    except:
      self.prop={}
  def __init__(self,page,prop):
    page.widgets.append(self)
    self.on_init()
    try:
      dictlib.merge(self.prop,prop)
    except:
      self.prop=prop
    self.label=ttk.Label(page.frame,
      text=self.prop["label"],
      font=(self.Config["font"]["family"],self.Config["font"]["size"]),
      foreground=self.Config["color"]["label"][0],
      background=self.Config["color"]["label"][1],
      anchor="e")
    self.label.grid(row=len(page.widgets),column=0,sticky="nsew")
    self.label.config(justify="right")
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
