from .widget import rtkWidget

import Tkinter as tk
import ttk

class rtkPub(rtkWidget):
  def __init__(self,page,prop):
    super(rtkPub,self).__init__(page,prop)
    self.io=tk.Button(page.frame,text="Do")
    self.io.grid(row=len(page.widgets),column=2,sticky="nsw")
  def reflesh(self):
    return
