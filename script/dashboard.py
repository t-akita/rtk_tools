#!/usr/bin/python

import numpy as np
import sys
import os
import time
import commands
import subprocess
import functools
import re

import roslib
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String

import Tkinter as tk
import tkMessageBox
import tkFileDialog as filedialog
from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename

from rtk_tools import dictlib

Config={
  "path":"~/",
  "label":{
    "confirm":"Stop anyway",
    "open":"Open",
    "save":"Save As"
  },
  "font":{
    "family":"System",
    "size":10
  },
  "color":{
    "background": "#00FF00",
    "lit": "#FF8800",
    "unlit": "#000000",
    "mask": "#666666"
  },
  "icon":{
    "logo":"logo.png",
    "recipe":"pan.png",
    "start":"start.png",
    "stop":"stop.png"
  }
}
Param={
  "recipe":""
}
Launches=[]
Indicates=[]

####recipe manager############
def cb_load(msg):
  Param["recipe"]=msg.data
  wRecipe.delete(0,tk.END)
  wRecipe.insert(0,Param["recipe"])
  if os.system("ls "+Config["path"]+"/recipe.d/"+Param["recipe"])==0:
    rospy.set_param("/dashboard",Param)
    commands.getoutput("cd "+Config["path"]+"; rm recipe; ln -s recipe.d/"+Param["recipe"]+" recipe")
    commands.getoutput("rosparam load "+Config["path"]+"/recipe/param.yaml")
    res=Bool(); res.data=True; pub_Y3.publish(res)
    pub_msg.publish("recipe_manager::cb_load "+Param["recipe"])
  else:
    pub_E3.publish(Bool())
    pub_msg.publish("recipe_manager::cb_load failed "+Param["recipe"])

def cb_open_dir():
  ret=askopendirname(parent=root,initialdir=Config["path"]+"/recipe.d",initialfile="")
  dir=re.sub(r".*/recipe.d","",ret)
  if dir != "":
    msg=String()
    msg.data=dir.replace("/","")
    cb_load(msg)

def cb_save():
  ret=asksaveasfilename(parent=root,defaultext="",initialdir=Config["path"]+"/recipe.d",initialfile="",filetypes=[("Directory", "*/")])
  if ret != "":
    print "save",ret

####launch manager############
msgBox=None
def cb_run(n):
  global Launches,msgBox
  if msgBox is not None:
    msgBox.destroy()
    msgBox=None
  item=Launches[n]
  if item["state"]==0:
    proc=subprocess.Popen(["roslaunch",item["package"],item["file"]])
    item["tag"]["foreground"]=litcolor
    item["tag"]["font"]=boldfont
    item["button"]["image"]=stopicon
    item["process"]=proc
    item["state"]=1
    set_timeout(functools.partial(cb_runstat,(n,2)),3)
  elif item["state"]==2:
    if "confirm" in item:
      if item["confirm"]:
        w=item["tag"]
        msgBox=tk.Tk()
        msgBox.title("Confirm")
        msgBox.geometry("100x30+"+str(w.winfo_rootx())+"+"+str(w.winfo_rooty()+30))
        try:
          f=tkMessageBox.askyesno("Confirm",Config["label"]["confirm"],parent=msgBox)
        except:
          print "Message box exception"
          f=False
        if msgBox is None: return
        msgBox.destroy()
        msgBox=None
        if f is False: return
    item["process"].terminate()
    item["state"]=3
    set_timeout(functools.partial(cb_stop,n),1)

def cb_runstat(tpl):
  global Launches
  item=Launches[tpl[0]]
  item["state"]=tpl[1]

def cb_stop(n):
  global Launches
  item=Launches[n]
  item["tag"]["foreground"]=unlitcolor
  item["tag"]["font"]=normalfont
  item["button"]["image"]=starticon
  item["state"]=0

####Indicator############
def cb_bool(n,msg):
  global Indicates
  item=Indicates[n]
  if msg.data:
    set_timeout(functools.partial(cb_turnon,n),0)
  else:
    if "sto" in item: clear_timeout(item["sto"])
    set_timeout(functools.partial(cb_turnoff,n),0)

def cb_turnon(n):
  global Indicates
  item=Indicates[n]
  item["tag"]["foreground"]=litcolor
  item["tag"]["font"]=boldfont
  if "sto" in item: clear_timeout(item["sto"])
  item["sto"]=set_timeout(functools.partial(cb_turnoff,n),item["timeout"])

def cb_turnoff(n):
  global Indicates
  item=Indicates[n]
  if "sto" in item: item.pop("sto")
  item["tag"]["foreground"]=unlitcolor
  item["tag"]["font"]=normalfont

####setTimeout
sto_time=0
sto_index=0
sto_tarray=[]
sto_farray=[]
def sto_reflesh():
  global sto_time,sto_index,sto_tarray,sto_farray
  if len(sto_tarray)>0:
    sto_time=min(sto_tarray)
    sto_index=sto_tarray.index(sto_time)
  else:
    sto_time=0
def set_timeout(cb,delay):
  global sto_time,sto_index,sto_tarray,sto_farray
  t=time.time()+delay
  sto_tarray.append(t)
  sto_farray.append(cb)
  sto_reflesh()
  return t
def clear_timeout(t):
  if len(sto_tarray)>0:
    try:
      idx=sto_tarray.index(t)
    except:
      print "sto id not found",t
    else:
      sto_tarray.pop(idx)
      sto_farray.pop(idx)
      sto_reflesh()
def sto_update():
  global sto_time,sto_index,sto_tarray,sto_farray
  if sto_time>0:
    if time.time()>sto_time:
      cb=sto_farray[sto_index]
      sto_tarray.pop(sto_index)
      sto_farray.pop(sto_index)
      sto_reflesh()
      cb()

####Message box
buffer=[]
def cb_sub(msg):
  buffer.append(msg.data)
def cb_log():
  if len(buffer)==0: return
  msg=""
  while len(buffer)>0:
    msg=msg+buffer.pop(0)+"\n"
  sub=tk.Tk()
  text=tk.Text(sub,width=100,height=20,background="#FFFFCC")
  text.pack(side='left',fill='y',anchor='nw')
  text.insert("1.0",msg)

########################################################
def parse_argv(argv):
  args={}
  for arg in argv:
    tokens = arg.split(":=")
    if len(tokens) == 2:
      key = tokens[0]
      args[key] = tokens[1]
  return args
########################################################
rospy.init_node("dashboard",anonymous=True)
try:
  dictlib.merge(Config,rospy.get_param("/config/dashboard"))
except Exception as e:
  print "get_param exception:",e.args
dictlib.merge(Config,parse_argv(sys.argv))

####sub pub
rospy.Subscriber("~load",String,cb_load)
rospy.Subscriber("/message",String,cb_sub)
pub_Y3=rospy.Publisher("~loaded",Bool,queue_size=1)
pub_E3=rospy.Publisher("~failed",Bool,queue_size=1)

####reflect file link to parameter server
if "path" in Config:
  ln=commands.getoutput("ls -l "+Config["path"]+"/recipe")
  if "->" in ln:
    dst=re.sub(r".*->","",ln)
    Param["recipe"]=re.sub(r".*/","",dst)
    rospy.set_param("/dashboard",Param)
  commands.getoutput("rosparam load "+Config["path"]+"/recipe/param.yaml")

####Layout####
normalfont=(Config["font"]["family"],Config["font"]["size"],"normal")
boldfont=(Config["font"]["family"],Config["font"]["size"],"bold")
bgcolor=Config["color"]["background"]
litcolor=Config["color"]["lit"]
unlitcolor=Config["color"]["unlit"]
maskcolor=Config["color"]["mask"]
iconpath=commands.getoutput("rospack find rtk_tools")+"/icon/"

root=tk.Tk()
root.title("Dashboard")
root.config(background=bgcolor)
root.config(bd=1)
root.geometry(str(root.winfo_screenwidth())+"x26+0+0")
root.rowconfigure(0,weight=1)
root.overrideredirect(True)

logoicon=tk.PhotoImage(file=iconpath+Config["icon"]["logo"])
recipeicon=tk.PhotoImage(file=iconpath+Config["icon"]["recipe"])
starticon=tk.PhotoImage(file=iconpath+Config["icon"]["start"])
stopicon=tk.PhotoImage(file=iconpath+Config["icon"]["stop"])
tk.Button(root,image=logoicon,bd=0,highlightthickness=0,command=cb_log).pack(side='left',anchor='nw',padx=(0,0))
tk.Label(root,image=recipeicon,bd=0,background=bgcolor).pack(side='left',fill='y',anchor='e',padx=(10,0))
wRecipe=tk.Entry(root,font=normalfont,width=10)
wRecipe.pack(side='left',fill='y')
wRecipe.insert(0,Param["recipe"])
tk.Button(root,text=Config["label"]["open"],command=cb_open_dir).pack(side='left',fill='y')
tk.Button(root,text=Config["label"]["save"],width=8,command=cb_save).pack(side='left',fill='y',padx=(0,20))

for key in Config.keys():
  if key.startswith('launch'):
    item=Config[key]
    n=len(Launches)
    wlabel=tk.Label(root,text=item["label"],font=normalfont,background=maskcolor,foreground=unlitcolor)
    wlabel.pack(side='left',fill='y',anchor='w')
    wbtn=tk.Button(root,image=starticon,bd=0,highlightthickness=0,command=functools.partial(cb_run,n))
    wbtn.pack(side='left',fill='y',anchor='w',padx=(0,10))
    item["tag"]=wlabel
    item["button"]=wbtn
    item["state"]=0
    if "auto" in item:
      set_timeout(functools.partial(cb_run,n),item["auto"])
    Launches.append(item)
  elif key.startswith('indic'):
    item=Config[key]
    n=len(Indicates)
    wlabel=tk.Label(root,text=item["label"],font=normalfont,background=maskcolor,foreground=unlitcolor)
    wlabel.pack(side='right',fill='y',anchor='e',padx=(0,5))
    item["tag"]=wlabel
    rospy.Subscriber(item["topic"],Bool,functools.partial(cb_bool,n))
    Indicates.append(item)

while not rospy.is_shutdown():
  sto_update()
  root.update()
