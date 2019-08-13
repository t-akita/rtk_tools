#!/usr/bin/python

import numpy as np
import yaml
import time
import sys

import Tkinter as tk
import ttk

import roslib
import rospy

from rtk_tools.ezui import rtkEzui
from rtk_tools import dictlib

Config={
  "geom":"300x750-0+0",
  "dump":"",
  "conf":"panel.ui",
  "lift":True,
  "label":{
    "button":"Save",
    "confirm":"Overwrite yaml"
  },
  "font":{
    "family":"System",
    "size":10
  },
  "color":{
    "background": "#00FF00"
  }
}

def cb_close():
  global panel
  panel=None
  print "panel close rq"
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
try:
  dictlib.merge(Config,rospy.get_param("/config/panel"))
except Exception as e:
  print "get_param exception:",e.args

dictlib.merge(Config,parse_argv(sys.argv))

####Layout####
root=tk.Tk()
ttk.Style(root).theme_use("clam")
root.title("panel")
root.protocol("WM_DELETE_WINDOW", cb_close)
root.config(background=Config["color"]["background"])

panel=rtkEzui(Config)
try:
  panel.same_on(root)
#  panel.top_on(root)
except:
  print "No config file"
  sys.exit(404)
print "loop start",time.time()-t0
while not rospy.is_shutdown():
  root.update()
  try:
    panel.update()
  except:
    sys.exit(0)

