#!/usr/bin/env python3

import numpy as np
import sys
import os
import time
import functools
import re
import socket

import roslib
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String

import tkinter as tk
from tkinter import ttk
from rtk_tools import dictlib
from rtk_tools import timeout

rospy.init_node("report",anonymous=True)
Config={
  "width":800,
  "rows":4,
  "altitude":-24,
  "font":{
    "family":"System",
    "size":10
  },
  "color":{
    "background": "#00FF00",
    "label": ("#FFFFFF","#555555"),
    "ok": ("#000000","#CCCCCC"),
    "ng": ("#FF0000","#CCCCCC")
  },
  "format":'{:.3g}',
  "delay": 1
}

Values={}    #Widget of Report table
Reports=0    #Subscribed Report count
Snap={}      #Log for one cycle
Logs=[]      #Log for life cycle
Gate=0

def to_report(dat):
  global Values,Reports,Snap,Gate
  if Reports>=1:
    for k,v in dat.items():
      if k in Values:
        Reports=Reports+1
        if(hasattr(v,"__iter__")):
          Snap[k]=v[0]
          Values[k][0].configure(text=str(Config["format"].format(v[0])))
          if(v[1]==0):
            Values[k][0].configure(foreground=okcolor[0])
            Values[k][0].configure(background=okcolor[1])
          else:
            Values[k][0].configure(foreground=ngcolor[0])
            Values[k][0].configure(background=ngcolor[1])
        else:
          Snap[k]=v
          Values[k][0].configure(text=str(Config["format"].format(v)))
          Values[k][0].configure(foreground=okcolor[0])
          Values[k][0].configure(background=okcolor[1])

def cb_report(s):
  ss=s.data[-1:-1]
  dic=eval(s.data)
  timeout.set(functools.partial(to_report,dic),0)

def to_update():
  global Values,Reports,Gate
  if Gate>0: to_complete()
  Gate=0
  if Reports==0:
    for row in Values.values():
      for i in range(len(row)-1,0,-1):
        row[i].configure(text=row[i-1].cget("text"))
      row[0].configure(text="")
      row[0]["text"]=""
  if Reports<=1:
    if "recipe" in Config:
      recipe=rospy.get_param(Config["recipe"])
      print("report update",recipe)
      if type(recipe) is str:
        Snap["__recipe__"]=recipe
      elif type(recipe) is dict:
        Snap["__recipe__"]=recipe["name"]
        recipe.pop("name")
        for key in recipe:
          Snap["__recipe__"]=Snap["__recipe__"]+":"+str(recipe[key])
      Values["__recipe__"][0].configure(text=Snap["__recipe__"])
    Reports=1
  Snap["__count__"]=len(Logs)+1
  Values["__count__"][0].configure(text=str(Snap["__count__"]))
  return
def cb_update(s):
  timeout.set(to_update,0)
def to_complete():
  global Reports
  if Reports>1:
    Reports=0
    ldat=[]
    for k in Config["keys"]:
      if k in Snap:
        ldat.append(Snap[k])
      else:
        ldat.append(np.nan)
    Logs.append(ldat)
def cb_complete(s):
  global Gate
  Gate=Gate+1

def cb_dump(s):
  global Reports
  to_complete()
  f=open('report_dump.txt', 'w')
  f.write(str(Config["labels"]).lstrip('[').rstrip(']')+"\n")
  map(lambda x:f.write(str(x).lstrip('[').rstrip(']')+"\n"),Logs)
#
#  for x in Logs:
#    f.write(str(x).lstrip('[').rstrip(']')+"\n")
#  f.close()
  return

##############
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
rospy.init_node("report",anonymous=True)
try:
  conf=rospy.get_param("/config/report")
except:
  conf={}
try:
  dictlib.merge(Config,conf)
except Exception as e:
  print("get_param exception:",e.args)

dictlib.merge(Config,parse_argv(sys.argv))

if "recipe" in Config:
  Config["keys"].insert(0,"__recipe__")
  Config["labels"].insert(0,"recipe")

Config["keys"].insert(0,"__count__")
Config["labels"].insert(0,"#")

####sub pub
rospy.Subscriber("/report",String,cb_report)
rospy.Subscriber("/report/update",Bool,cb_update)
rospy.Subscriber("/report/complete",Bool,cb_complete)
rospy.Subscriber("/report/dump",Bool,cb_dump)

####Layout####
rows=int(Config["rows"])
font=(Config["font"]["family"],Config["font"]["size"],"normal")
bgcolor=Config["color"]["background"]
lbcolor=Config["color"]["label"]
okcolor=Config["color"]["ok"]
ngcolor=Config["color"]["ng"]

root=tk.Tk()
root.client(socket.gethostname())
root.title("Report")
root.geometry(str(Config["width"])+"x100+0"+str(Config["altitude"]))
frame=tk.Frame(root,bd=2,background=bgcolor)
frame.pack(fill='x',anchor='n',expand=1)

Values={}
for n,s in enumerate(Config["labels"]):
  frame.columnconfigure(n,weight=1)
  label=ttk.Label(frame,text=s,font=font,foreground=lbcolor[0],background=lbcolor[1],anchor='c')
  label.grid(row=0,column=n,padx=1,pady=1,sticky='nsew')
  k=Config["keys"][n]
  Values[k]=[]
  for i in range(rows):
    label=ttk.Label(frame,font=font,foreground=okcolor[0],background=okcolor[1],anchor='e')
    label.grid(row=i+1,column=n,padx=1,pady=1,sticky='nsew')
    label.configure(text='')
    Values[k].append(label)

#if len(Displays)>0: timeout.set(functools.partial(cb_display,0),1)

while not rospy.is_shutdown():
  timeout.update()
  root.update()
  rospy.sleep(0.1)
