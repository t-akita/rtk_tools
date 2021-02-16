#!/usr/bin/env python3

import numpy as np
import yaml
import time
import re
import sys

import tkinter as tk
from tkinter import ttk

import roslib
import rospy

from rtk_tools.ezui import rtkEzui
from rtk_tools import dictlib

Config={
  "geom":"300x750-0+0",
  "dump":"",
  "conf":"panel.ui",
  "lift":False,
  "message":{
    "save":"Overwrite"
  },
  "width":(0,10),
  "font":{
    "family":"System",
    "size":10
  },
  "color":{
    "background": "#00FF00",
    "title": ("#FFFFFF","#555555"),
    "label": ("#000000","#CCCCCC")
  }
}

def cb_close():
  global panel
  panel=None
  print("panel close rq")
  return

################
def parse_argv(argv):
  args={}
  for arg in argv:
    tokens = arg.split(":=")
    if len(tokens) == 2:
      key = tokens[0]
      if re.match(r'\([ ]*([0-9.]+,[ ]*)*[0-9.]+[ ]*\)$',tokens[1]):
        # convert tuple-like-string to tuple
        args[key]=eval(tokens[1])
        continue
      args[key]=tokens[1]
  return args
####ROS Init####
t0=time.time()
rospy.init_node("rtk_panel",anonymous=True)
try:
  conf=rospy.get_param("/config/panel")
except:
  conf={}
else:
  cset=["label","title"]
  for k in cset:
    if k in conf["color"]:
      conf["color"][k]=eval(conf["color"][k])
      print("color tuple",k,conf["color"][k])
try:
  dictlib.merge(Config,conf)
except Exception as e:
  print("get_param exception:",e.args)

dictlib.merge(Config,parse_argv(sys.argv))

####Layout####
root=tk.Tk()
ttk.Style(root).theme_use("clam")
root.title(rospy.get_name())
root.protocol("WM_DELETE_WINDOW", cb_close)
root.config(background=Config["color"]["background"])

panel=rtkEzui(Config)
try:
  panel.same_on(root)
#  panel.top_on(root)
except Exception as e:
  print("panel open error",e.args)
  sys.exit(404)
print("loop start",time.time()-t0)
while not rospy.is_shutdown():
  root.update()
  try:
    panel.update()
  except Exception as e:
    print("panel update exception",e.args)
    sys.exit(0)
  time.sleep(0.01)

