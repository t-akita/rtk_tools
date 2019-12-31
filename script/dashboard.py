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
#import tkFileDialog as filedialog
from tkfilebrowser import askopendirname
from rtk_tools.filebrowser import asksaveasfilename
from rtk_tools import dictlib
from dashlog import dashLog

Config={
#  "recipe":{"link": "recipe","dir": "recipe.d"},
  "confirm":"Stop anyway",
  "autoclose":10,
  "altitude":"+0",
  "font":{"family":"System", "size":10},
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
    "stop":"stop.png",
    "open":"open.png",
    "copy":"copy.png"
  }
}
Param={
  "recipe":""
}
Launches=[]
Indicates=[]

####dialog box control########
msgBox=None
msgBoxWait=None
def cb_autoclose():
  global msgBox,msgBoxWait
  if msgBoxWait is not None: msgBox.destroy()
  msgBoxWait=None
####recipe manager############
def cb_wRecipe(s):
  wRecipe.delete(0,tk.END)
  wRecipe.insert(0,s)
def cb_load(msg):
  Param["recipe"]=msg.data
  set_timeout(functools.partial(cb_wRecipe,Param["recipe"]),0)
  if os.system("ls "+dirpath+"/"+Param["recipe"])==0:
    rospy.set_param("/dashboard",Param)
    commands.getoutput("rm "+linkpath+";ln -s "+dirpath+"/"+Param["recipe"]+" "+linkpath)
    commands.getoutput("rosparam load "+linkpath+"/param.yaml")
    res=Bool(); res.data=True; pub_Y3.publish(res)
    pub_msg.publish("recipe_manager::cb_load "+Param["recipe"])
  else:
    pub_E3.publish(Bool())
    pub_msg.publish("recipe_manager::cb_load failed "+Param["recipe"])

def cb_open_dir():
  global msgBox,msgBoxWait
  if msgBoxWait is not None: return
  msgBox=tk.Tk()
  msgBox.title("Load Recipe")
  msgBoxWait=msgBox.after(Config["autoclose"]*1000,cb_autoclose)
  ret=askopendirname(parent=msgBox,initialdir=dirpath,initialfile="")
  if msgBoxWait is None: return  #returned by autoclose
  msgBox.after_cancel(msgBoxWait)
  msgBoxWait=None
  msgBox.destroy()
  dir=re.sub(r".*"+Config["recipe"]["dir"],"",ret)
  if dir != "":
    msg=String()
    msg.data=dir.replace("/","")
    cb_load(msg)

def cb_save_as():
  global msgBox,msgBoxWait
  if msgBoxWait is not None: return
  msgBox=tk.Tk()
  msgBox.title("Save Recipe as")
  msgBoxWait=msgBox.after(Config["autoclose"]*1000,cb_autoclose)
  ret=asksaveasfilename(parent=msgBox,defaultext="",initialdir=dirpath,initialfile="",filetypes=[("Directory", "*/")])
  if msgBoxWait is None: return  #returned by autoclose
  msgBox.after_cancel(msgBoxWait)
  msgBoxWait=None
  msgBox.destroy()
  if ret != "":
    dir=re.sub(r".*"+Config["recipe"]["dir"],"",ret)
    recipe=dir.replace("/","")
    commands.getoutput("cp -a "+dirpath+"/"+Param["recipe"]+" "+dirpath+"/"+recipe)
    Param["recipe"]=recipe
    wRecipe.delete(0,tk.END)
    wRecipe.insert(0,Param["recipe"])
    commands.getoutput("rm "+linkpath+";ln -s "+dirpath+"/"+Param["recipe"]+" "+linkpath)

####launch manager############
def cb_run(n):
  global Launches,msgBox,msgBoxWait
  if msgBoxWait is not None: return
  item=Launches[n]
  if item["state"]==0:
    if ".launch" in item["file"]:
      cmd=["roslaunch",item["package"],item["file"]];
    else:
      cmd=["xterm","-e","rosrun",item["package"],item["file"]];
    if "args" in item:
      for k in item["args"]:
        cmd.append(k+":="+str(item["args"][k]))
    proc=subprocess.Popen(cmd)
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
        msgBoxWait=msgBox.after(Config["autoclose"]*1000,cb_autoclose)
        msg=Config["confirm"]
        if "message" in Config:
          if "halt" in Config["message"]: msg=Config["message"]["halt"]
          elif "launch" in Config["message"]: msg=Config["message"]["launch"]
        elif "label" in Config:
          if "confirm" in Config["label"]: msg=Config["label"]["confirm"]
        f=tkMessageBox.askyesno("Confirm",msg,parent=msgBox)
        if msgBoxWait is None: return
        msgBox.after_cancel(msgBoxWait)
        msgBoxWait=None
        msgBox.destroy()
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
sto_tarray=[]
sto_farray=[]
def sto_reflesh():
  global sto_time,sto_tarray,sto_farray
  if len(sto_tarray)>0:
    sto_time=min(sto_tarray)
  else:
    sto_time=0
def set_timeout(cb,delay):
  global sto_time,sto_tarray,sto_farray
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
      print "sto::clear id not found",t
    else:
      sto_tarray.pop(idx)
      sto_farray.pop(idx)
      sto_reflesh()
def sto_update():
  global sto_time,sto_tarray,sto_farray
  if sto_time>0:
    if time.time()>sto_time:
      try:
        idx=sto_tarray.index(sto_time)
      except:
        print "sto::update id not found",sto_time
      else:
        cb=sto_farray[idx]
        sto_tarray.pop(idx)
        sto_farray.pop(idx)
        sto_reflesh()
        cb()

####Message box
mbox=dashLog("+0+300",150,"#0000CC","#FFFFFF")
ebox=dashLog("+0+50",90,"#CC0000","#FFFFFF")
def cb_mbox_push(n,msg):
  if n==0:
    set_timeout(functools.partial(mbox.push,msg),0)
  else:
    set_timeout(functools.partial(ebox.push,msg),0)
def cb_mbox_pop():
  mbox.popup()
  ebox.popup()

########################################################
rospy.init_node("dashboard",anonymous=True)
try:
  dictlib.merge(Config,rospy.get_param("/config/dashboard"))
except Exception as e:
  print "get_param exception:",e.args
thispath=commands.getoutput("rospack find rtk_tools")
if "load" in Config:
  commands.getoutput("rosparam load "+thispath+"/../"+Config["load"])
if "recipe" in Config:
  linkpath=thispath+"/../"+Config["recipe"]["link"]
  dirpath=thispath+"/../"+Config["recipe"]["dir"]
try:
  dictlib.merge(Config,rospy.get_param("/config/dashboard"))
except Exception as e:
  print "get_param exception:",e.args

####sub pub
rospy.Subscriber("~load",String,cb_load)
rospy.Subscriber("/message",String,functools.partial(cb_mbox_push,0))
rospy.Subscriber("/error",String,functools.partial(cb_mbox_push,2))
pub_Y3=rospy.Publisher("~loaded",Bool,queue_size=1)
pub_E3=rospy.Publisher("~failed",Bool,queue_size=1)
pub_msg=rospy.Publisher("/message",String,queue_size=1)

####Layout####
normalfont=(Config["font"]["family"],Config["font"]["size"],"normal")
boldfont=(Config["font"]["family"],Config["font"]["size"],"bold")
bgcolor=Config["color"]["background"]
litcolor=Config["color"]["lit"]
unlitcolor=Config["color"]["unlit"]
maskcolor=Config["color"]["mask"]
iconpath=thispath+"/icon/"

root=tk.Tk()
root.title("Dashboard")
root.config(background=bgcolor)
root.config(bd=1)
root.geometry(str(root.winfo_screenwidth())+"x26+0"+Config["altitude"])
root.rowconfigure(0,weight=1)
root.overrideredirect(True)

logoicon=tk.PhotoImage(file=iconpath+Config["icon"]["logo"])
recipeicon=tk.PhotoImage(file=iconpath+Config["icon"]["recipe"])
starticon=tk.PhotoImage(file=iconpath+Config["icon"]["start"])
stopicon=tk.PhotoImage(file=iconpath+Config["icon"]["stop"])
openicon=tk.PhotoImage(file=iconpath+Config["icon"]["open"])
copyicon=tk.PhotoImage(file=iconpath+Config["icon"]["copy"])
tk.Button(root,image=logoicon,bd=0,background=bgcolor,highlightthickness=0,command=cb_mbox_pop).pack(side='left',anchor='nw',padx=(0,0))
if "recipe" in Config:
  ln=commands.getoutput("ls -l "+linkpath)
  if "->" in ln:
    dst=re.sub(r".*->","",ln)
    Param["recipe"]=re.sub(r".*/","",dst)
    rospy.set_param("/dashboard",Param)
  commands.getoutput("rosparam load "+linkpath+"/param.yaml")
  tk.Label(root,image=recipeicon,bd=0,background=bgcolor).pack(side='left',fill='y',anchor='e',padx=(10,0))
  wRecipe=tk.Entry(root,font=normalfont,width=10)
  wRecipe.pack(side='left',fill='y')
  wRecipe.insert(0,Param["recipe"])
  tk.Button(root,image=openicon,bd=0,background=bgcolor,highlightthickness=0,command=cb_open_dir).pack(side='left',fill='y',padx=(0,5))
  tk.Button(root,image=copyicon,bd=0,background=bgcolor,highlightthickness=0,command=cb_save_as).pack(side='left',fill='y',padx=(0,30))

for key in Config.keys():
  if key.startswith('launch'):
    item=Config[key]
    if "file" not in item: continue
    n=len(Launches)
    wlabel=tk.Label(root,text=item["label"],font=normalfont,background=maskcolor,foreground=unlitcolor)
    wlabel.pack(side='left',fill='y',anchor='w')
    wbtn=tk.Button(root,image=starticon,background=bgcolor,bd=0,highlightthickness=0,command=functools.partial(cb_run,n))
    wbtn.pack(side='left',fill='y',anchor='w',padx=(0,10))
    item["tag"]=wlabel
    item["button"]=wbtn
    item["state"]=0
    if "auto" in item:
      if item["auto"]>=0:
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
  time.sleep(0.01)
