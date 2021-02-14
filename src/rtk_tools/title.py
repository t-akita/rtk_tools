from .widget import rtkWidget

import tkinter as tk
from tkinter import ttk

class rtkTitle(rtkWidget):
  def __init__(self,page,prop):
    super(rtkTitle,self).__init__(page,prop)
    self.label.config(foreground=self.Config["color"]["title"][0])
    self.label.config(background=self.Config["color"]["title"][1])
    self.label.config(anchor='w')
    self.label.grid_forget()
    self.label.grid(row=len(page.widgets),column=0,columnspan=2,sticky="nsew",pady=(3,0))
  def on_timeout(self):
    pass

