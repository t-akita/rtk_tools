import yaml
import time
import collections

import Tkinter as tk
import ttk

import rospy
import roslib

from .widget import rtkWidget
from .page import rtkPage
from .text import rtkText
from .number import rtkNumber
from .echo import rtkEcho
from .pub import rtkPub
from .title import rtkTitle

class rtkEzui(object):
  def __init__(self):
    self.prop={
      "geom":"300x750-0+0",
      "dump":"",
      "conf":"panel.ui"
    }
    return
  def top_on(self,root):
    pane=tk.Toplevel(root)
    pane.geometry(self.prop["geom"])
    self.same_on(pane)
  def same_on(self,pane):
    self.pane=pane
    page=rtkPage(self.pane)
    f=open(self.prop["conf"],'r')
    for line in f:
      try:
        prop=eval("{"+line+"}")
      except:
        rospy.logwarn("ezui::eval exception "+line)
        continue
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
    ttk.Button(self.ctrl,text="Save",command=lambda: self.cb_save(self.prop["dump"])).grid(row=1,column=3,padx=1,pady=1,sticky='nsew')
    rtkPage.show(0)
    self.ctrl.pack(fill='x',anchor='sw',expand=1)

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

  def cross(self,DCT,dct):
    for k,v in DCT.iteritems():
      if isinstance(DCT[k], dict) and (k in dct and isinstance(dct[k], dict)):
        self.cross(DCT[k],dct[k])
      elif k in dct:
        DCT[k]=dct[k]

  def cb_save(self,filename):
    print "cb_save",filename
    try:
      yf=open(filename, "r")
    except:
      rospy.logwarn("ezui::open exception "+filename)
      return
    try:
      param=yaml.load(yf)
    except:
      yf.close()
      rospy.logwarn("ezui::parser exception")
      return
    yf.close()
    try:
      yf=open(filename,"w")
      self.cross(param,rtkWidget.Param)
      yaml.dump(param,yf,default_flow_style=False)
    except:
      rospy.logwarn("ezui::dump exception")
    yf.close()

  def update(self):
    self.pane.lift()
    rtkPage.update()

