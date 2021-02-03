#!/usr/bin/python
 
import numpy as np
import sys
import os
import copy
import time
import yaml
import commands
import subprocess
import functools
import re
from collections import OrderedDict
 
import roslib
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String
 
import Tkinter as tk
import pymsgbox
from tkfilebrowser import askopendirname
from rtk_tools.filebrowser import asksaveasfilename
from rtk_tools import dictlib
from dashlog import dashLog
from rtk_tools import timeout
 
Config=OrderedDict([
  ("confirm","Stop anyway"),
  ("autoclose",10),
  ("altitude","+0"),
  ("font",{"family":"System", "size":10}),
  ("color",{
    "background": "#00FF00",
    "lit": "#FF8800",
    "unlit": "#000000",
    "mask": "#666666"
  }),
  ("display",{
    "color":{
      "background": "#FFFF00",
      "foreground": "#0000FF"
    }
  }),
  ("icon",{
    "logo":"logo.png",
    "recipe":"pan.png",
    "start":"start.png",
    "stop":"stop.png",
    "open":"open.png",
    "copy":"copy.png",
    "redraw":"pencil.png",
  }),
  ("password","admin")
])
Param={
  "recipe":""
}
Launches=[]
Indicates=[]
Displays=[]
Buttons=[]
RecipeName=''
 
####dialog box control########
msgBox=None
msgBoxWait=None
def cb_lift():
  if msgBox is not None:
    for k in msgBox.children:
        msgBox.children[k].lift()
  msgBoxWait=msgBox.after(500,cb_lift)
def cb_wait_nop():
  msgBoxWait=msgBox.after(1000,cb_wait_nop)

####recipe manager############
def set_param_sync(name,dat):
  for k in dat:
    org=rospy.get_param(name+'/'+k)
    if isinstance(dat[k],dict):
      dictlib.merge(org,dat[k])
    else:
      org=dat[k]
    rospy.set_param(name+'/'+k,org)

def cb_wRecipe(rc):
  if wRecipe is None: return
  wRecipe.delete(0,tk.END)
  wRecipe.insert(0,rc)

def cb_load(msg):
  global Param,RecipeName
  if wRecipe is None: return
  Param["recipe"]=msg.data
  recipe=msg.data.split(':')
  RecipeName=recipe[0]
  timeout.set(functools.partial(cb_wRecipe,Param["recipe"]),0)
  if os.system("ls "+dirpath+"/"+RecipeName)==0:
    set_param_sync("/dashboard",Param)
    commands.getoutput("rm "+linkpath)
    commands.getoutput("ln -s "+dirpath+"/"+RecipeName+" "+linkpath)
    commands.getoutput("rosparam load "+linkpath+"/param.yaml")
    if len(recipe)>1:
      commands.getoutput("rosparam load "+linkpath+"/"+str(recipe[1])+".yaml")
    pub_Y3.publish(mTrue)
  else:
    pub_E3.publish(mFalse)

def cb_open_dir():
  global msgBox,msgBoxWait
  if wRecipe is None: return
  if msgBoxWait is not None: return
  msgBox=tk.Toplevel()
  msgBox.title("Load Recipe")
  msgBox.withdraw()
  msgBoxWait=msgBox.after(1000,cb_wait_nop)
  ret=askopendirname(parent=root,initialdir=dirpath,initialfile="")
  msgBox.after_cancel(msgBoxWait)
  msgBoxWait=None
  msgBox.destroy()
  dir=re.sub(r".*"+Config["recipe"]["dir"],"",ret)
  if dir != "":
    msg=String()
    msg.data=dir.replace("/","")
    cb_load(msg)
 
def cb_save_as():
  global RecipeName,msgBox,msgBoxWait
  if wRecipe is None: return
  if msgBoxWait is not None: return
  msgBox=tk.Toplevel()
  msgBox.title("Save Recipe as")
  msgBox.withdraw()
  msgBoxWait=msgBox.after(1000,cb_wait_nop)
  ret=asksaveasfilename(parent=root,defaultext="",initialdir=dirpath,initialfile="",filetypes=[("Directory", "*/")])
  msgBox.after_cancel(msgBoxWait)
  msgBoxWait=None
  msgBox.destroy()
  if ret != "":
    dir=re.sub(r".*"+Config["recipe"]["dir"],"",ret)
    recipe=dir.replace("/","")
    commands.getoutput("cp -a "+dirpath+"/"+RecipeName+" "+dirpath+"/"+recipe)
    RecipeName=recipe
    Param["recipe"]=RecipeName
    rospy.set_param("/dashboard",Param)
    wRecipe.delete(0,tk.END)
    wRecipe.insert(0,Param["recipe"])
    commands.getoutput("rm "+linkpath+";ln -s "+dirpath+"/"+RecipeName+" "+linkpath)
 
####launch manager############
def cb_run(n):
  global Launches,msgBox,msgBoxWait
  if msgBoxWait is not None: return
  item=Launches[n]
  if item["state"]==0:
    fg=True
    if "pass" in item:
      fg=False
      alert=""
      w=item["tag"]
      msgBox=tk.Toplevel()
      geom="300x130+"+str(w.winfo_rootx())+"+"+str(w.winfo_rooty()+25)
      msgBox.geometry(geom)
      msgBoxWait=msgBox.after(1000,cb_wait_nop)
      msg="Enter password"
      result=pymsgbox.password(root=msgBox,text=msg,geom=geom)
      if result[0].startswith('O'): #OK
        if result[1]==Config["password"]:
          fg=True
        else:
          alert="password is incorrect"
      elif not result[0].startswith("C"):  #Cancel
        alert="enter password error"
      if alert:
        msgBox.after_cancel(msgBoxWait)
        msgBox.destroy()
        msgBox=tk.Toplevel()
        msgBox.geometry("250x100+"+str(w.winfo_rootx())+"+"+str(w.winfo_rooty()))
        msgBoxWait=msgBox.after(500,cb_lift)
        pymsgbox.alert(root=msgBox,text=alert)
      msgBox.after_cancel(msgBoxWait)
      msgBoxWait=None
      msgBox.destroy()
    if fg:
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
      timeout.set(functools.partial(cb_runstat,n),3)
      if "pre" in item:
        print "dash pre",item["pre"]
        subprocess.Popen(item["pre"].split())
  elif item["state"]==2:
    if "confirm" in item:
      if item["confirm"]:
        w=item["tag"]
        msgBox=tk.Toplevel()
        msgBox.geometry("250x100+"+str(w.winfo_rootx())+"+"+str(w.winfo_rooty()))
        msgBoxWait=msgBox.after(500,cb_lift)
        msg=item["label"]+Config["confirm"]
        if "message" in Config:
          if "halt" in Config["message"]: msg=Config["message"]["halt"]
          elif "launch" in Config["message"]: msg=Config["message"]["launch"]
        elif "label" in Config:
          if "confirm" in Config["label"]: msg=Config["label"]["confirm"]
        msg=item["label"]+msg
        f=pymsgbox.confirm(root=msgBox,text=msg,buttons=['OK','CANCEL'])
        msgBox.after_cancel(msgBoxWait)
        msgBoxWait=None
        msgBox.destroy()
        if f.startswith("C"):  #Cancel
          return
    item["process"].terminate()
    item["state"]=3
    timeout.set(functools.partial(cb_stop,n),1)
 
def cb_runstat(n):
  global Launches
  item=Launches[n]
  if item["state"]==1:
    item["state"]=2
    timeout.set(functools.partial(cb_runstat,n),1)
  elif item["state"]==2:
    if item["process"].poll() is None:
      timeout.set(functools.partial(cb_runstat,n),1)
    else:
      item["state"]=3
      timeout.set(functools.partial(cb_stop,n),0)
 
def cb_stop(n):
  global Launches
  item=Launches[n]
  item["tag"]["foreground"]=unlitcolor
  item["tag"]["font"]=normalfont
  item["button"]["image"]=starticon
  item["state"]=0
  if "post" in item:
    subprocess.Popen(item["post"].split())
 
shutdown=False
def cb_shutdown(msg):
  global shutdown
  for item in Launches:
    if item["state"]==2:
      item["process"].terminate()
  rospy.sleep(1)
  shutdown=True
 
####Redraw############
def cb_redraw():
  timeout.set(lambda: pub_redraw.publish(mTrue),0)
 
####Indicator############
def cb_indicator(n,msg):
  global Indicates
  item=Indicates[n]
  if msg.data:
    timeout.set(functools.partial(cb_turnon,n),0)
  else:
    if "sto" in item: timeout.clear(item["sto"])
    timeout.set(functools.partial(cb_turnoff,n),0)
 
def cb_turnon(n):
  global Indicates
  item=Indicates[n]
  item["tag"]["foreground"]=litcolor
  item["tag"]["font"]=boldfont
  if "sto" in item: timeout.clear(item["sto"])
  item["sto"]=timeout.set(functools.partial(cb_turnoff,n),item["timeout"])
 
def cb_turnoff(n):
  global Indicates
  item=Indicates[n]
  if "sto" in item: item.pop("sto")
  item["tag"]["foreground"]=unlitcolor
  item["tag"]["font"]=normalfont
 
####Display parametr############
def cb_display(n):
  global Displays
  item=Displays[n]
  widget=item["tag"]
  val=item["label"]
  try:
    val_name=str(rospy.get_param(item["name"]))
    if val_name == "":
      val_name='---'
    val+=val_name
  except Exception:
    val+='---'
  if val!=widget["text"]:
    widget.configure(text=val)
  n=n+1
  if n>=len(Displays): n=0
  timeout.set(functools.partial(cb_display,n),0.5)
 
####Button############
def cb_button(n):
  global Buttons,msgBox,msgBoxWait
  if msgBoxWait is not None: return
  item=Buttons[n]
  w=item["button"]
  f=True
  if item["confirm"]:
    msgBox=tk.Toplevel()
    msgBox.geometry("250x100+"+str(w.winfo_rootx())+"+"+str(w.winfo_rooty()))
    msgBoxWait=msgBox.after(500,cb_lift)
    msg=item["message"]
    f=pymsgbox.confirm(root=msgBox,text=msg,buttons=['OK','NO','CANCEL'])
    msgBox.after_cancel(msgBoxWait)
    msgBoxWait=None
    msgBox.destroy()

    pub_msg=Bool()
    if f.startswith('C'): #Cancel
      print "Button cancel:",item["label"]
    else:
      if f.startswith('O'): #OK
        pub_msg.data=True
      rospy.loginfo("Button='%s' topic=%d",item["label"], pub_msg.data)
      item["pub"].publish(pub_msg)
  else:
    rospy.loginfo("Button='%s' topic=1",item["label"])
    item["pub"].publish(mTrue)

def cb_butt_enable(n,msg):
  timeout.set(functools.partial(cb_button_enable,n,msg.data),0)

def cb_button_enable(n,enable):
  if enable:
    item["button"]['state'] = tk.NORMAL
    item["button"]["background"]=litcolor
    if "sto" in item: timeout.clear(item["sto"])
    item["sto"]=timeout.set(functools.partial(cb_button_enable,n,False),item["timeout"])
  else:
    item["button"]['state'] = tk.DISABLED
    item["button"]["background"]=maskcolor
    if "sto" in item: item.pop("sto")

####Message box
mbox=dashLog("+0+300",150,"#0000CC","#FFFFFF")
ebox=dashLog("+0+50",90,"#CC0000","#FFFFFF")
def cb_mbox_push(n,msg):
  if n==0:
    timeout.set(functools.partial(mbox.push,msg),0)
  else:
    timeout.set(functools.partial(ebox.push,msg),0)
def cb_mbox_pop():
  mbox.popup()
  ebox.popup()

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
dictlib.merge(Config,parse_argv(sys.argv))
thispath=commands.getoutput("rospack find rtk_tools")
init_load=None
if "load" in Config:
  init_load=Config["load"]
  yamlpath=thispath+"/../"+Config["load"]
  yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
      lambda loader, node: OrderedDict(loader.construct_pairs(node)))
  try:
    conf=yaml.load(file(yamlpath))
    commands.getoutput("rosparam load "+yamlpath)
  except:
    conf={}
  try:
    dictlib.merge(Config,conf["config"]["dashboard"])
  except Exception as e:
    print "first load marge error:",e.args
try:
  dictlib.merge(Config,rospy.get_param("/config/dashboard"))
except Exception as e:
  print "get_param exception:",e.args

if "load" in Config:
  if init_load != Config["load"]:
    yamlpath=thispath+"/../"+Config["load"]
    try:
      conf=yaml.load(file(yamlpath))
      commands.getoutput("rosparam load "+yamlpath)
    except:
      conf={}
    try:
      dictlib.merge(Config,conf["config"]["dashboard"])
    except Exception as e:
      print "second load marge error:",e.args
if "recipe" in Config:
  srcpath=re.subn(r".*?/","/",thispath[::-1],1)[0][::-1]
  dirpath=srcpath+Config["recipe"]["dir"]
  linkpath=srcpath+Config["recipe"]["link"]
  print "dirpath",dirpath
  print "linkpath",linkpath
try:
  dictlib.merge(Config,rospy.get_param("/config/dashboard"))
except Exception as e:
  print "get_param exception:",e.args
 
####Bools
mTrue=Bool()
mTrue.data=True
mFalse=Bool()
 
####sub pub
rospy.Subscriber("~load",String,cb_load)
rospy.Subscriber("/message",String,functools.partial(cb_mbox_push,0))
rospy.Subscriber("/error",String,functools.partial(cb_mbox_push,2))
rospy.Subscriber("/shutdown",Bool,cb_shutdown)
pub_Y3=rospy.Publisher("~loaded",Bool,queue_size=1)
pub_E3=rospy.Publisher("~failed",Bool,queue_size=1)
pub_msg=rospy.Publisher("/message",String,queue_size=1)
pub_redraw=rospy.Publisher("/request/redraw",Bool,queue_size=1)
 
####Layout####
normalfont=(Config["font"]["family"],Config["font"]["size"],"normal")
boldfont=(Config["font"]["family"],Config["font"]["size"],"bold")
bgcolor=Config["color"]["background"]
litcolor=Config["color"]["lit"]
unlitcolor=Config["color"]["unlit"]
maskcolor=Config["color"]["mask"]
dispattr=Config["display"];Config.pop("display")  #Patch to display
 
root=tk.Tk()
root.title("Dashboard")
root.config(background=bgcolor)
root.config(bd=1)
root.geometry(str(root.winfo_screenwidth())+"x26+0"+Config["altitude"])
root.rowconfigure(0,weight=1)
root.attributes('-topmost', True)
root.attributes('-type', 'splash')
 
####ICONS####
iconpath=thispath+"/icon/"
logoicon=tk.PhotoImage(file=iconpath+Config["icon"]["logo"])
recipeicon=tk.PhotoImage(file=iconpath+Config["icon"]["recipe"])
starticon=tk.PhotoImage(file=iconpath+Config["icon"]["start"])
stopicon=tk.PhotoImage(file=iconpath+Config["icon"]["stop"])
openicon=tk.PhotoImage(file=iconpath+Config["icon"]["open"])
copyicon=tk.PhotoImage(file=iconpath+Config["icon"]["copy"])
redrawicon=tk.PhotoImage(file=iconpath+Config["icon"]["redraw"])
tk.Button(root,image=logoicon,bd=0,background=bgcolor,highlightthickness=0,command=cb_mbox_pop).pack(side='left',anchor='nw',padx=(0,0))
if "recipe" in Config:
  ln=commands.getoutput("ls -l "+linkpath)
  if "->" in ln:
    dst=re.sub(r".*->","",ln)
    RecipeName=re.sub(r".*/","",dst)
    Param["recipe"]=RecipeName
    rospy.set_param("/dashboard",Param)
  commands.getoutput("rosparam load "+dirpath+"/"+RecipeName+"/param.yaml")
  tk.Label(root,image=recipeicon,bd=0,background=bgcolor).pack(side='left',fill='y',anchor='e',padx=(10,0))
  wRecipe=tk.Entry(root,font=normalfont,width=10)
  wRecipe.pack(side='left',fill='y')
  wRecipe.insert(0,RecipeName)
  tk.Button(root,image=openicon,bd=0,background=bgcolor,highlightthickness=0,command=cb_open_dir).pack(side='left',fill='y',padx=(0,5))
  tk.Button(root,image=copyicon,bd=0,background=bgcolor,highlightthickness=0,command=cb_save_as).pack(side='left',fill='y',padx=(0,30))
else:
  wRecipe=None
 
ckeys=Config.keys()
for key in ckeys:
  if key.startswith('launch'):
    item=Config[key]
    if "file" not in item: continue
    n=len(Launches)
    print "item",item
    wlabel=tk.Label(root,text=item["label"],font=normalfont,background=maskcolor,foreground=unlitcolor)
    wlabel.pack(side='left',fill='y',anchor='w')
    wbtn=tk.Button(root,image=starticon,background=bgcolor,bd=0,highlightthickness=0,command=functools.partial(cb_run,n))
    wbtn.pack(side='left',fill='y',anchor='w',padx=(0,10))
    item["tag"]=wlabel
    item["button"]=wbtn
    item["state"]=0
    if "auto" in item:
      if item["auto"]>=0:
        timeout.set(functools.partial(cb_run,n),item["auto"])
    Launches.append(item)
 
tk.Button(root,image=redrawicon,bd=0,background=bgcolor,highlightthickness=0,command=cb_redraw).pack(side='right',anchor='nw',padx=(0,0))
#ckeys.sort(reverse=True)
for key in ckeys:
  if key.startswith('indic'):
    item=Config[key]
    n=len(Indicates)
    wlabel=tk.Label(root,text=item["label"],font=normalfont,background=maskcolor,foreground=unlitcolor)
    wlabel.pack(side='right',fill='y',anchor='e',padx=(0,5))
    item["tag"]=wlabel
    rospy.Subscriber(item["topic"],Bool,functools.partial(cb_indicator,n))
    Indicates.append(item)
  elif key.startswith('disp'):
    item=Config[key]
    print "item",item
    n=len(Displays)
    wlabel=tk.Label(root,font=boldfont,background=dispattr["color"]["background"],foreground=dispattr["color"]["foreground"])
    wlabel.pack(side='right',fill='y',anchor='e',padx=(0,5))
    item["tag"]=wlabel
    Displays.append(item)
  elif key.startswith('butt'):
    item=Config[key]
    n=len(Buttons)
    wbtn=tk.Button(root,text=item["label"],font=normalfont,background=maskcolor,foreground=unlitcolor,bd=0,highlightthickness=0,command=functools.partial(cb_button,n))
    wbtn.pack(side='right',fill='y',anchor='w',padx=(0,10))
    item["button"]=wbtn
    item["state"]=0
    item["pub"]=rospy.Publisher(item["topic"],Bool,queue_size=1)
    if "en_default" in item:
      if item["en_default"]:
        item["button"]['state']=tk.NORMAL
      else:
        item["button"]['state']=tk.DISABLED
    else:
      item["button"]['state']=tk.NORMAL
    if "en_topic" in item:
      rospy.Subscriber(item["en_topic"],Bool,functools.partial(cb_butt_enable,n))
      item["button"]['state']=tk.DISABLED
      if "timeout" not in item:
        item["timeout"]=1
    Buttons.append(item)
 
if len(Displays)>0: timeout.set(functools.partial(cb_display,0),1)
 
while not rospy.is_shutdown():
  if shutdown: break
  timeout.update()
  root.update()
  time.sleep(0.01)
