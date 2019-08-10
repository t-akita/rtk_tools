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
Config=parse_argv(sys.argv)

####Layout####
root=tk.Tk()
ttk.Style(root).theme_use("clam")
root.title("panel")
root.protocol("WM_DELETE_WINDOW", cb_close)
#root.overrideredirect(True)

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

