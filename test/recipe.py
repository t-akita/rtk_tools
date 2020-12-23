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
  "icon":{
    "open":"open.png",
  },
  "format":'{:.3g}',
  "delay": 1
}

####recipe manager############
def cb_load(msg):
  global Param,RecipeName
#  if wRecipe is None: return
#  Param["recipe"]=msg.data
  recipe=msg.data.split(':')
  RecipeName=recipe[0]
  timeout.set(functools.partial(cb_wRecipe,Param["recipe"]),0)
#  if os.system("ls "+dirpath+"/"+RecipeName)==0:
#    set_param_sync("/dashboard",Param)
#    commands.getoutput("rm "+linkpath)
#    commands.getoutput("ln -s "+dirpath+"/"+RecipeName+" "+linkpath)
#    commands.getoutput("rosparam load "+linkpath+"/param.yaml")
#    if len(recipe)>1:
#      commands.getoutput("rosparam load "+linkpath+"/"+str(recipe[1])+".yaml")
#    pub_Y3.publish(mTrue)
#  else:
#    pub_E3.publish(mFalse)

def cb_edit(msg):
  global Param,RecipeName
#  if wRecipe is None: return
#  Param["recipe"]=msg.data
  recipe=msg.data.split(':')
  RecipeName=recipe[0]
  rospy.logerr("edit RecipeName='%s'", RecipeName)
  pub_edit.publish(RecipeName)

def cb_ret_x0(result):
  if result==True:
    rospy.logerr("X0 OK")
  else:
    rospy.logerr("X0 NG")

def cb_ret_load(result):
  if result==True:
    pub_x0.publish(False)
  else:
    rospy.logerr("Recipe load error")

def cb_ret_save(result):
  if result==True:
    rospy.logerr("Recipe save ok")
  else:
    rospy.logerr("Recipe save error")

def cb_ret_edit(result):
  if result==True:
    pub_x0.publish(False)
  else:
    rospy.logerr("Recipe edit error")

def cb_ret_delete(result):
  if result==True:
    rospy.logerr("Recipe delete ok")
  else:
    rospy.logerr("Recipe delete error")

def cb_edit(msg):
  global Param,RecipeName
#  if wRecipe is None: return
#  Param["recipe"]=msg.data
  recipe=msg.data.split(':')
  RecipeName=recipe[0]
  rospy.logerr("edit RecipeName='%s'", RecipeName)
  pub_edit.publish(RecipeName)

def cb_delete(msg):
  global Param,RecipeName
#  if wRecipe is None: return
#  Param["recipe"]=msg.data
  recipe=msg.data.split(':')
  RecipeName=recipe[0]
  rospy.logerr("delete RecipeName='%s'", RecipeName)
  pub_delete.publish(RecipeName)

def cb_copy_from(msg):
  global Param,RecipeName
#  if wRecipe is None: return
#  Param["recipe"]=msg.data
  recipe=msg.data.split(':')
  RecipeName=recipe[0]
  wCopyFrom.delete(0,tk.END)
  wCopyFrom.insert(0,RecipeName)

def cb_copy():
  from_name=wCopyFrom.get()
  from_dirpath=dirpath+"/"+from_name
  to_name=wCopyTo.get()
  to_dirpath=dirpath+"/"+to_name
  if os.path.exists(from_dirpath) == False:
    rospy.logerr("Copy folder does not exist RecipeName='%s'", from_name)
  elif os.path.exists(to_dirpath) == True:
    rospy.logerr("Copy destination folder exists RecipeName='%s'", to_name)
  else:
    rospy.logerr("copy RecipeName from='%s' to='%s'", from_name, to_name)
    commands.getoutput("cp -a "+dirpath+"/"+from_name+" "+dirpath+"/"+to_name)

def cb_new(msg):
  global Param,RecipeName
#  if wRecipe is None: return
#  Param["recipe"]=msg.data
  recipe=msg.data.split(':')
  RecipeName=recipe[0]
  rospy.logerr("new RecipeName='%s'", RecipeName)
  pub_save.publish(RecipeName)

def cb_open_dir(name):
#  rospy.logerr("recipe_d='%s'", dirpath)
#  if wRecipe is None: return
  ret=askopendirname(parent=root,title=name,initialdir=dirpath,initialfile="",okbuttontext=name)
  dir=re.sub(r".*"+Config["dump_prefix"],"",ret)
  if dir != "":
    msg=String()
    msg.data=dir.replace("/","")
    if name == 'Load':
      cb_load(msg)
    elif name == 'Edit':
      cb_edit(msg)
    elif name == 'Delete':
      cb_delete(msg)
    elif name == 'CopySelect':
      cb_copy_from(msg)


def cb_save_as(name):
  global RecipeName
#  if wRecipe is None: return
  ret=asksaveasfilename(parent=root,title="save",defaultext="",initialdir=dirpath,initialfile="",filetypes=[("Directory", "*/")],okbuttontext="ok")
  dir=re.sub(r".*"+Config["dump_prefix"],"",ret)
  if dir != "":
    if name == 'SaveAs':
      recipe=dir.replace("/","")
      commands.getoutput("cp -a "+dirpath+"/"+RecipeName+" "+dirpath+"/"+recipe)
      RecipeName=recipe
      Param["recipe"]=RecipeName
      rospy.set_param("/dashboard",Param)
      wRecipe.delete(0,tk.END)
      wRecipe.insert(0,Param["recipe"])
      commands.getoutput("rm "+linkpath+";ln -s "+dirpath+"/"+RecipeName+" "+linkpath)
    elif name == 'New':
      msg=String()
      msg.data=dir.replace("/","")
      cb_new(msg)

def cb_default_recipe():
  rospy.logerr("default Recipe='%s'", '')
  pub_load.publish('')

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
rospy.Subscriber('/wpc/Y0',Bool,cb_ret_x0)
rospy.Subscriber('/recipe/loaded',Bool,cb_ret_load)
rospy.Subscriber('/recipe/saved',Bool,cb_ret_save)
rospy.Subscriber('/recipe/edited',Bool,cb_ret_edit)
rospy.Subscriber('/recipe/deleted',Bool,cb_ret_delete)
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
root.geometry(str(Config["width"])+"x100+1250"+str(Config["altitude"]))
root.attributes("-topmost", True)
frame=tk.Frame(root,bd=2,background=bgcolor)
frame.pack(fill='x',anchor='n',expand=1)

####ICONS####
iconpath=thispath+"/icon/"
openicon=tk.PhotoImage(file=iconpath+Config["icon"]["open"])

#tk.Button(root,text='open',bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_open_dir,'Load')).pack(side='left',fill='y',padx=(0,5))
#tk.Button(root,text='copy',bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_save_as,'SaveAs')).pack(side='left',fill='y',padx=(0,5))
tk.Button(root,text='edit',bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_open_dir,'Edit')).pack(side='left',fill='y',padx=(0,5))
tk.Button(root,text='delete',bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_open_dir,'Delete')).pack(side='left',fill='y',padx=(0,5))
tk.Button(root,text='new',bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_save_as,'New')).pack(side='left',fill='y',padx=(0,5))
tk.Button(root,text='default',bd=0,background=bgcolor,highlightthickness=0,command=cb_default_recipe).pack(side='left',fill='y',padx=(0,5))

tk.Button(root,text='copy',bd=0,background=bgcolor,highlightthickness=0,command=cb_copy).pack(side='left',fill='y',padx=(0,5))
wlabel=tk.Label(root,text='Copy From:',font=font,foreground=lbcolor[0],background=lbcolor[1])
wlabel.pack(side='left',fill='y',anchor='e',padx=(0,5))
wCopyFrom=tk.Entry(root,font=font,width=20)
wCopyFrom.pack(side='left',fill='y')
wCopyFrom.insert(0,"")
tk.Button(root,image=openicon,bd=0,background=bgcolor,highlightthickness=0,command=functools.partial(cb_open_dir,'CopySelect')).pack(side='left',fill='y',padx=(0,5))
wlabel=tk.Label(root,text='Copy To:',font=font,foreground=lbcolor[0],background=lbcolor[1])
wlabel.pack(side='left',fill='y',anchor='e',padx=(0,5))
wCopyTo=tk.Entry(root,font=font,width=20)
wCopyTo.pack(side='left',fill='y')
wCopyTo.insert(0,"")

while not rospy.is_shutdown():
#  timeout.update()
  try:
    root.update()
  except Exception as e:
    print "recipe update exception",e.args
    sys.exit(0)
  time.sleep(1)
