from .widget import rtkWidget

import Tkinter as tk
import ttk
import time

class rtkPage(object):
  pages=[]
  pageNo=0
  def __init__(self,root):
    self.pages.append(self)
    self.widgets=[]
    self.frame=tk.Frame(root,bd=2,background=root["background"])
    self.frame.columnconfigure(1,weight=1)
  @staticmethod
  def update():
    for w in rtkPage.pages[rtkPage.pageNo].widgets:
      w.update(time.time())
  @staticmethod
  def show(diff):
    if diff==0:
      rtkPage.pages[rtkPage.pageNo].frame.pack(fill='x',anchor='nw',expand=1)
    elif diff>0:
      if rtkPage.pageNo>=len(rtkPage.pages)-1: return
      rtkPage.pages[rtkPage.pageNo].frame.pack_forget()
      rtkPage.pageNo=rtkPage.pageNo+1
      rtkPage.pages[rtkPage.pageNo].frame.pack(fill='x',anchor='nw',expand=1)
    else:
      if rtkPage.pageNo<=0: return
      rtkPage.pages[rtkPage.pageNo].frame.pack_forget()
      rtkPage.pageNo=rtkPage.pageNo-1
      rtkPage.pages[rtkPage.pageNo].frame.pack(fill='x',anchor='nw',expand=1)
