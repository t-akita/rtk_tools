from .widget import rtkWidget

import Tkinter as tk
import ttk

class rtkEcho(rtkWidget):
  def __init__(self,page,prop):
    super(rtkEcho,self).__init__(page,prop)
    self.io=tk.Text(page.frame,width=16,height=1+prop["label"].count("\n"))
    self.io.grid(row=len(page.widgets),column=2,sticky="nsw")
  def reflesh(self):
    return
