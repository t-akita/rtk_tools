import yaml
import time
import copy

import Tkinter as tk
import ttk
import tkMessageBox

import rospy
import roslib

from .widget import rtkWidget
from .page import rtkPage
from .text import rtkText
from .number import rtkNumber
from .echo import rtkEcho
from .pub import rtkPub
from .title import rtkTitle
from . import dictlib

class rtkEzui(object):
  def __init__(self,conf):
    self.prop={
      "geom":"300x750-0+0",
      "dump":"",
      "conf":"panel.ui",
      "lift":True,
      "label":{
        "button":"Save",
        "confirm":"Overwrite yaml",
      },
      "font":{
        "family":"System",
        "size":10
      },
      "color":{
        "background": "#AAAAAA"
      }
    }
    dictlib.merge(self.prop,conf)
    if type(self.prop["lift"]) is str: self.prop["lift"]=eval(self.prop["lift"])
    cf=copy.copy(conf)
    cf.pop("geom")
    cf.pop("dump")
    cf.pop("conf")
    cf.pop("lift")
    dictlib.merge(rtkPage.Config,cf)
    dictlib.merge(rtkWidget.Config,cf)
    return
  def top_on(self,root):
    pane=tk.Toplevel(root)
    pane.geometry(self.prop["geom"])
    self.same_on(pane)
  def same_on(self,pane):
    pane.geometry(self.prop["geom"])
    self.pane=pane
    page=rtkPage(self.pane)
    f=open(self.prop["conf"],'r')
    lines=f.readlines()
    for n,line in enumerate(lines):
      try:
        print "Parsing conf file",n,line
        prop=eval("{"+line+"}")
      except:
        continue
      if "class" not in prop: continue
      if prop["class"]=="Title":
        if "page" in prop:
          if prop["page"]=="break":
            page=rtkPage(self.pane)
      try:
        print "Parsing class",n,prop
        w=eval("rtk"+prop["class"]+"(page,prop)")
      except:
        continue
    f.close()
    self.ctrl=tk.Frame(self.pane,bd=2,background='#444444')
    self.ctrl.columnconfigure(1,weight=1)
    self.ctrl.columnconfigure(2,weight=1)
    self.ctrl.columnconfigure(3,weight=1)
    ttk.Button(self.ctrl,text="<<<",command=self.cb_pagebwd).grid(row=1,column=1,padx=1,pady=1,sticky='nsew')
    ttk.Button(self.ctrl,text=">>>",command=self.cb_pagefwd).grid(row=1,column=2,padx=1,pady=1,sticky='nsew')
    ttk.Button(self.ctrl,text=self.prop["label"]["button"],command=lambda: self.cb_save(self.prop["dump"])).grid(row=1,column=3,padx=1,pady=1,sticky='nsew')
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

  def cb_save(self,filename):
    f=tkMessageBox.askyesno("Confirm",self.prop["label"]["confirm"])
    if f is False: return
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
      dictlib.cross(param,rtkWidget.Param)
      yaml.dump(param,yf,default_flow_style=False)
    except:
      rospy.logwarn("ezui::dump exception")
    yf.close()

  def update(self):
    if self.prop["lift"]: self.pane.lift()
    rtkPage.update()

