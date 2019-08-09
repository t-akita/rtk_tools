import yaml
import time

import Tkinter as tk
import ttk

from .widget import rtkWidget
from .page import rtkPage
from .text import rtkText
from .number import rtkNumber
from .echo import rtkEcho
from .pub import rtkPub
from .title import rtkTitle

class rtkEzui(object):
  def __init__(self):
    return
  def top_on(self,root,filename):
    pane=tk.Toplevel(root)
#    pane.overrideredirect(True)
    pane.geometry("300x750-0+0")
    self.same_on(pane,filename)
  def same_on(self,pane,filename):
    self.pane=pane
    page=rtkPage(self.pane)
    f=open(filename,'r')
    for line in f:
      prop=eval("{"+line+"}")
      if "class" not in prop: continue
      if prop["class"]=="Title":
        if "page" in prop:
          if prop["page"]=="break":
            page=rtkPage(self.pane)
      w=eval("rtk"+prop["class"]+"(page,prop)")
    f.close()
    self.ctrl=tk.Frame(self.pane,bd=2,background='#444444')
    self.ctrl.columnconfigure(1,weight=1)
    self.ctrl.columnconfigure(2,weight=1)
    self.ctrl.columnconfigure(3,weight=1)
    ttk.Button(self.ctrl,text="<<<",command=self.cb_pagebwd).grid(row=1,column=1,padx=1,pady=1,sticky='nsew')
    ttk.Button(self.ctrl,text=">>>",command=self.cb_pagefwd).grid(row=1,column=2,padx=1,pady=1,sticky='nsew')
    ttk.Button(self.ctrl,text="Save",command=self.cb_save).grid(row=1,column=3,padx=1,pady=1,sticky='nsew')
    rtkPage.show(0)
    self.ctrl.pack(fill='x',anchor='sw',expand=1)
    print "Ezui pack"

  def cb_pagefwd(self):
    if rtkPage.pageNo<len(rtkPage.pages)-1:
      self.ctrl.pack_forget()
      rtkPage.show(1)
      self.ctrl.pack(fill='x',anchor='sw',expand=1)

  def cb_pagebwd(self):
    if rtkPage.pageNo>0:
      self.ctrl.pack_forget()
      rtkPage.show(-1)
      self.ctrl.pack(fill='x',anchor='sw',expand=1)

  def cb_save(self):
     return

  def update(self):
    self.pane.lift()
    rtkPage.update()

