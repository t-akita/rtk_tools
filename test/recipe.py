#!/usr/bin/python

import numpy as np
import sys
import os
import time
import commands
import functools
import re

import roslib
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String

import Tkinter as tk
import ttk
from tkfilebrowser import askopendirname
from rtk_tools.filebrowser import asksaveasfilename
from rtk_tools.filebrowser import asksaveasfilename
from rtk_tools import dictlib
#import timeout
#import const

Config={
  "width":800,
  "rows":4,
  "altitude":"+0",
  "font":{"family":"System", "size":10},
  "color":{
    "background": "#00FF00",
    "label": ("#FFFFFF","#555555"),
    "ok": ("#000000","#CCCCCC"),
    "ng": ("#FF0000","#CCCCCC")
  },
  "format":'{:.3g}',
  "delay": 1,
  "pub_delay": 0.1,
  "sub_timeout": 10.0
}

Buttons=[]
CurrentItem={}
Publishs={}
Entrys={}

####recipe manager############
def cb_publish_recipe(event):
  set_publish_recipe()

def cb_publish_x0(event):
  rospy.logerr("%s RecipeName='%s' X0 send", CurrentItem["name"], RecipeName)
  pub_x0.publish(False)

def set_publish_recipe():
  rospy.logerr("%s RecipeName='%s' send", CurrentItem["name"], RecipeName)
  CurrentItem["pub"].publish(RecipeName)

def set_recipe(name,n):
  global CurrentItem,RecipeName
  RecipeName=name
  CurrentItem=Buttons[n]
  if "pub" in CurrentItem:
    rospy.logerr("%s RecipeName='%s' start", CurrentItem["name"], RecipeName)
    if "s_topic" in CurrentItem:
      rospy.Timer(rospy.Duration(Config["pub_delay"]), cb_publish_recipe, True)
      try:
        result=rospy.wait_for_message(CurrentItem["s_topic"],Bool,timeout=Config["sub_timeout"])
        if result.data:
          rospy.logerr("%s RecipeName='%s' ok", CurrentItem["name"], RecipeName)
          if "p_next" in CurrentItem:
            rospy.Timer(rospy.Duration(Config["pub_delay"]), cb_publish_x0, True)
            try:
              result=rospy.wait_for_message('/wpc/Y0',Bool,timeout=Config["sub_timeout"])
              if result.data:
                rospy.logerr("%s RecipeName='%s' X0 ok", CurrentItem["name"], RecipeName)
              else:
                rospy.logerr("%s RecipeName='%s' X0 error", CurrentItem["name"], RecipeName)
            except rospy.ROSException as e:
              rospy.logerr("%s RecipeName='%s' X0 timeout", CurrentItem["name"], RecipeName)
        else:
          rospy.logerr("%s RecipeName='%s' error", CurrentItem["name"], RecipeName)
      except rospy.ROSException as e:
        rospy.logerr("%s RecipeName='%s' timeout", CurrentItem["name"], RecipeName)
    else:
      set_publish_recipe()

def cb_copy_from():
  Entrys["CopyFrom"].delete(0,tk.END)
  Entrys["CopyFrom"].insert(0,RecipeName)

def cb_copy(n):
  from_name=Entrys["CopyFrom"].get()
  from_dirpath=dirpath+"/"+from_name
  to_name=Entrys["CopyTo"].get()
  to_dirpath=dirpath+"/"+to_name
  if os.path.exists(from_dirpath) == False:
    rospy.logerr("Copy folder does not exist RecipeName='%s'", from_name)
  elif os.path.exists(to_dirpath) == True:
    rospy.logerr("Copy destination folder exists RecipeName='%s'", to_name)
  else:
    set_recipe(to_name,n)
    rospy.logerr("copy RecipeName from='%s' to='%s'", from_name, to_name)
    commands.getoutput("cp -a "+dirpath+"/"+from_name+" "+dirpath+"/"+to_name)

def cb_open_dir(n):
  name=Buttons[n]["name"]
  ret=askopendirname(parent=root,title=name,initialdir=dirpath,initialfile="",okbuttontext=name)
  dir=re.sub(r".*"+Config["dump_prefix"],"",ret)
  if dir != "":
    data=dir.replace("/","")
    recipe=data.split(':')
    set_recipe(recipe[0],n)
    if name == 'CopySelect':
      cb_copy_from()

def cb_save_as(n):
  name=Buttons[n]["name"]
  ret=asksaveasfilename(parent=root,title=name,defaultext="",initialdir=dirpath,initialfile="",filetypes=[("Directory", "*/")],okbuttontext="Ok")
  dir=re.sub(r".*"+Config["dump_prefix"],"",ret)
  if dir != "":
    data=dir.replace("/","")
    recipe=data.split(':')
    set_recipe(recipe[0],n)

def cb_default_recipe(n):
  set_recipe('',n)

def cb_button(n):
  func=Buttons[n]["func"]
  if func == 'open':
    cb_open_dir(n)
  elif func == 'save':
    cb_save_as(n)
  elif func == 'default':
    cb_default_recipe(n)
  elif func == 'copy':
    cb_copy(n)

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
rospy.init_node("recipe",anonymous=True)
try:
  conf=rospy.get_param("/config/recipe")
except:
  conf={}
try:
  dictlib.merge(Config,conf)
except Exception as e:
  print "get_param exception:",e.args

dictlib.merge(Config,parse_argv(sys.argv))

dirpath=Config["dump_prefix"]
thispath=commands.getoutput("rospack find rtk_tools")

####sub pub
pub_x0=rospy.Publisher('/wpc/X0',Bool,queue_size=1)
pub_load=rospy.Publisher('/recipe/load',String,queue_size=1)
pub_save=rospy.Publisher('/recipe/save',String,queue_size=1)
pub_edit=rospy.Publisher('/recipe/edit',String,queue_size=1)
pub_delete=rospy.Publisher('/recipe/delete',String,queue_size=1)

####Layout####
rows=int(Config["rows"])
font=(Config["font"]["family"],Config["font"]["size"],"normal")
bgcolor=Config["color"]["background"]
lbcolor=Config["color"]["label"]
okcolor=Config["color"]["ok"]
ngcolor=Config["color"]["ng"]

root=tk.Tk()
root.title("Recipe")
root.geometry(str(Config["width"])+"x30+1250"+str(Config["altitude"]))
root.attributes("-topmost", True)
frame=tk.Frame(root,bd=2,background=bgcolor)
frame.pack(fill='x',anchor='n',expand=1)

####ICONS####
iconpath=thispath+"/icon/"

# p_topic topic_type is String type and Recipe Name only
# p_next  publishe topic '/wpc/X0'
# s_topic topic_type is Bool and False only
f=open(Config["dump_conf"],'r')
lines=f.readlines()
for n,line in enumerate(lines):
  try:
    prop=eval("{"+line+"}")
  except:
    continue
  if "class" not in prop: continue
  if prop["class"] == 'Button':
    item={}
    n=len(Buttons)
    item=prop
    if "p_topic" in prop:
      if prop["p_topic"] not in Publishs:
        Publishs[prop["p_topic"]]=rospy.Publisher(prop["p_topic"],String,queue_size=1)
      item["pub"]=Publishs[prop["p_topic"]]
    if "icon" in prop:
      icon=tk.PhotoImage(file=iconpath+prop["icon"])
      item["button"]=tk.Button(root,image=icon,bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_button,n)).pack(side='left',fill='y',padx=(0,5))
    else:
      item["button"]=tk.Button(root,text=prop["name"],bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_button,n)).pack(side='left',fill='y',padx=(0,5))
    print "recipe item ",n,item
    Buttons.append(item)
  elif prop["class"] == 'Label':
    wlabel=tk.Label(root,text=prop["name"]+':',font=font,foreground=lbcolor[0],background=lbcolor[1])
    wlabel.pack(side='left',fill='y',anchor='e',padx=(0,5))
  elif prop["class"] == 'Entry':
    Entrys[prop["name"]]=tk.Entry(root,font=font,width=20)
    Entrys[prop["name"]].pack(side='left',fill='y')
    Entrys[prop["name"]].insert(0,"")
f.close()

while not rospy.is_shutdown():
#  timeout.update()
  try:
    root.update()
  except Exception as e:
    print "recipe update exception",e.args
    sys.exit(0)
  time.sleep(1)
