#!/usr/bin/python

import numpy as np
import yaml
import time
import sys

import roslib
import rospy

import Tkinter as tk
import ttk
from rtk_tools.widget import rtkWidget
from rtk_tools.page import rtkPage
from rtk_tools.text import rtkText
from rtk_tools.number import rtkNumber
from rtk_tools.echo import rtkEcho
from rtk_tools.pub import rtkPub
from rtk_tools.title import rtkTitle

def loadwidget(filename):
  page=rtkPage(root)
  f=open(filename,'r')
  for line in f:
    prop=eval("{"+line+"}")
    if "class" not in prop: continue
    if prop["class"]=="Title":
      if "page" in prop:
        if prop["page"]=="break":
          page=rtkPage(root)
    w=eval("rtk"+prop["class"]+"(page,prop)")
  f.close()

def cb_pagefwd():
  if rtkPage.pageNo<len(rtkPage.pages)-1:
    ctrl.pack_forget()
    rtkPage.show(1)
    ctrl.pack(fill='x',anchor='sw',expand=1)

def cb_pagebwd():
  if rtkPage.pageNo>0:
    ctrl.pack_forget()
    rtkPage.show(-1)
    ctrl.pack(fill='x',anchor='sw',expand=1)

def cb_save():
   return

def cb_close():
  rtkPage.pageNo=-1
  return

################
def parse_argv(argv):
  args={}
  for arg in argv:
    tokens = arg.split(":=")
    if len(tokens) == 2:
      key = tokens[0]
      args[key]=tokens[1]
  return args
####ROS Init####
t0=time.time()
rospy.init_node("rtk_panel",anonymous=True)
Config=parse_argv(sys.argv)

####Layout####
root=tk.Tk()
ttk.Style(root).theme_use("clam")
root.title("panel")
root.geometry("300x800+0+0")
root.protocol("WM_DELETE_WINDOW", cb_close)

if "conf" in Config:
  loadwidget(Config["conf"])
else:
  loadwidget("panel.ui")

print "file loaded",time.time()-t0

ctrl=tk.Frame(root,bd=2,background='#444444')
ctrl.columnconfigure(1,weight=1)
ctrl.columnconfigure(2,weight=1)
ctrl.columnconfigure(3,weight=1)
ttk.Button(ctrl,text="<<<",command=cb_pagebwd).grid(row=1,column=1,padx=1,pady=1,sticky='nsew')
ttk.Button(ctrl,text=">>>",command=cb_pagefwd).grid(row=1,column=2,padx=1,pady=1,sticky='nsew')
ttk.Button(ctrl,text="Save",command=cb_save).grid(row=1,column=3,padx=1,pady=1,sticky='nsew')

rtkPage.show(0)
ctrl.pack(fill='x',anchor='sw',expand=1)

print "loop start",time.time()-t0
while rtkPage.pageNo>=0 and not rospy.is_shutdown():
  root.update()
  rtkPage.update()

