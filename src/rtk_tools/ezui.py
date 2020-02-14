import yaml
import time
import copy
import commands
import functools
import os

import Tkinter as tk
import ttk
import tkMessageBox

import rospy
import roslib

from . import dictlib
from .widget import rtkWidget
from .page import rtkPage
from .text import rtkText
from .number import rtkNumber
from .echo import rtkEcho
from .pub import rtkPub
from .title import rtkTitle
from .popup import rtkPopup
from . import dictlib

class rtkEzui(object):
  larricon=None
  rarricon=None
  saveicon=None
  def __init__(self,conf):
    self.prop={
      "geom":"300x750-0+0",
      "dump":"",
      "dump_prefix":"",
      "dump_dir@":"",
      "dump_ver@":"",
      "conf":"panel.ui",
      "lift":True,
      "weight": (2, 1),
      "message":{
        "save":"Overwrite yaml",
      },
      "font":{
        "family":"System",
        "size":10
      },
      "color":{
        "background": "#AAAAAA"
      },
      "icon":{
        "larr":"go-previous.png",
        "rarr":"go-next.png",
        "save":"save.png"
      },
      "Pub":{
        "icon":"run.png",
        "confirm":False,
        "message":""
      },
      "Text":{
        "message":"Reload the original string"
      },
      "Number":{
        "message":"Reload the original value"
      }
    }
    dictlib.merge(self.prop,conf)
    if type(self.prop["lift"]) is str: self.prop["lift"]=eval(self.prop["lift"])
    cf=copy.copy(conf)
    if "geom" in cf: cf.pop("geom")
    if "dump" in cf: cf.pop("dump")
    if "dump_pefix" in cf: cf.pop("dump_prefix")
    if "dump_dir@" in cf: cf.pop("dump_dir@")
    if "dump_ver@" in cf: cf.pop("dump_ver@")
    if "conf" in cf: cf.pop("conf")
    if "lift" in cf: cf.pop("lift")
    dictlib.merge(rtkPage.Config,cf)
    dictlib.merge(rtkWidget.Config,cf)

  def filepath(self):
    path=self.prop["dump_prefix"]
    try:
      path=path+"/"+rospy.get_param(self.prop["dump_dir@"])
    except Exception as e:
      rospy.logwarn("dump_dir@ error")
    try:
      subdir=os.listdir(path)
      subdir=filter(lambda f:os.path.isdir(os.path.join(path,f)),subdir)
      subdir.sort()
      path=path+"/"+subdir[int(rospy.get_param(self.prop["dump_ver@"]))]
    except Exception as e:
      rospy.logwarn("dump_ver@ error")
    if len(path)>0: path=path+"/"+self.prop["dump"]
    else: path=self.prop["dump"]
    print "ezui::filepath",path
    return path

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
      print "ezui::parsing line ",n
      try:
        prop=eval("{"+line+"}")
      except:
        continue
      if "class" not in prop: continue
      if prop["class"]=="Title":
        if "page" in prop:
          if prop["page"]=="break":
            page=rtkPage(self.pane)
      pdef={}
      if prop["class"] in self.prop:
        pdef=copy.copy(self.prop[prop["class"]])
      dictlib.merge(pdef,prop)
      try:
        w=eval("rtk"+prop["class"]+"(page,pdef)")
      except:
        continue
    f.close()
    self.ctrl=tk.Frame(self.pane,bd=2,background='#444444')
    self.ctrl.columnconfigure(0,weight=1)
    self.ctrl.columnconfigure(1,weight=1)
    self.ctrl.columnconfigure(2,weight=1)
    iconpath=commands.getoutput("rospack find rtk_tools")+"/icon/"
    if self.larricon is None:
      self.larricon=tk.PhotoImage(file=iconpath+self.prop["icon"]["larr"])
    if self.rarricon is None:
      self.rarricon=tk.PhotoImage(file=iconpath+self.prop["icon"]["rarr"])
    if self.saveicon is None:
      self.saveicon=tk.PhotoImage(file=iconpath+self.prop["icon"]["save"])
    tk.Button(self.ctrl,image=self.larricon,command=self.cb_pagebwd).grid(row=0,column=0,padx=1,pady=1,sticky='nsew')
    tk.Button(self.ctrl,image=self.rarricon,command=self.cb_pagefwd).grid(row=0,column=1,padx=1,pady=1,sticky='nsew')
    tk.Button(self.ctrl,image=self.saveicon,command=self.cb_save).grid(row=0,column=2,padx=1,pady=1,sticky='nsew')
    rtkPage.show(0)
    self.ctrl.pack(fill='x',anchor='sw',expand=1)
    try:
      filename=self.filepath()
      yf=open(filename, "r")
      rtkWidget.Origin=yaml.load(yf)
      yf.close()
    except:
      rospy.logwarn("ezui::origin parameter load error "+filename)
      return

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
    filename=self.filepath()
    f=tkMessageBox.askyesno("Confirm",self.prop["message"]["save"])
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
      rtkWidget.Origin=param
    except:
      rospy.logwarn("ezui::dump exception")
    yf.close()

  def update(self):
    if self.prop["lift"]: self.pane.lift()
    rtkPage.update()

