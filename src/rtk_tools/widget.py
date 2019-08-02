import Tkinter as tk
import ttk

class rtkWidget(object):
  Param={}
  def __init__(self,page,prop):
    page.widgets.append(self)
    self.prop=prop
    self.label=ttk.Label(page.frame,text=prop["label"],background='#CCCCCC',anchor="e")
    self.label.grid(row=len(page.widgets),column=1,sticky="nsew")
  def reflesh(self):
    return
