#!/usr/bin/env python3

import numpy as np
import sys
import os
import time
import subprocess
import functools
import re

import roslib
import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String

import tkinter as tk
from tkinter import messagebox
#import ttk
from tkfilebrowser import askopendirname
from rtk_tools.filebrowser import asksaveasfilename
from rtk_tools import dictlib
from rtk_tools import timeout

Config={
  "geom":"365x195+1210+150",
  "font":{"family":"System", "size":10},
  "color":{
    "button": "#00AAFF"
  },
  "format":'{:.3g}',
  "pub_delay": 0.1,
  "sub_timeout": 10.0,
  "stat_timeout": 1.0
}

####recipe manager############
def cb_publish_recipe(event):
  set_publish_recipe()

def cb_publish_x0(event):
  rospy.loginfo("Recipe:send=clear")
  pub_x0.publish(mFalse)

def set_publish_recipe():
  rospy.loginfo("Recipe:send=%s", exec_item["p_topic"])
  pub_msg = String()
  pub_msg.data = recipe_name
  exec_item["pub"].publish(pub_msg)

def set_event(pub_func, topic):
  msg_type = ""
  rospy.Timer(rospy.Duration(Config["pub_delay"]), pub_func, True)
  try:
    ret = rospy.wait_for_message(topic, Bool, timeout=Config["sub_timeout"])
    if ret.data:
      msg_type = "ok"
    else:
      msg_type = "ng"
  except rospy.ROSInterruptException as e:
    msg_type = ""
  except rospy.ROSException as e:
    msg_type = "timeout"
  if msg_type:
    rospy.loginfo("Recipe:result=%s [%s]", topic, msg_type)
  return msg_type

def set_recipe(name,n):
  global exec_item, recipe_name, massage
  func_ret = True
  msg_type = ""
  recipe_name = name
  exec_item = buttons[n]
  if "pub" in exec_item:
    rospy.loginfo("Recipe:%s RecipeName='%s' start", exec_item["name"], recipe_name)
    if "s_topic" in exec_item:
      msg_type = set_event(cb_publish_recipe, exec_item["s_topic"])
      if msg_type == "ok":
        if "p_next" in exec_item:
          msg_type = set_event(cb_publish_x0, '~cleared')
    else:
      set_publish_recipe()
      msg_type = "ok"
    if msg_type != "ok":
      func_ret = False
  if msg_type in MSG_TBL:
    if exec_item["name"] == 'Default':
      msg = ''
    else:
      msg = 'RecipeName:' + recipe_name + '\n'
    massage = msg + exec_item["name"] + ' ' + MSG_TBL[msg_type]
  return func_ret

def cb_copy_from():
  entrys["CopyFrom"].delete(0,tk.END)
  entrys["CopyFrom"].insert(0,recipe_name)

def cb_copy(n):
  global massage
  func_ret = False
  from_name = entrys["CopyFrom"].get()
  from_dirpath = dirpath + '/' + from_name
  to_name = entrys["CopyTo"].get()
  to_dirpath = dirpath + '/' + to_name
  if not from_name:
    massage = 'Copy From RecipeName Empty'
  elif not to_name:
    massage = 'Copy To RecipeName Empty'
  elif not os.path.exists(from_dirpath):
    massage = 'RecipeName:' + from_name + '\n' + 'Copy From folder does not exist'
    rospy.logerr("Recipe:Copy From dir does not exist RecipeName='%s'", from_name)
  elif os.path.exists(to_dirpath):
    massage = 'RecipeName:' + to_name + '\n' + 'Copy To folder exist'
    rospy.logerr("Recipe:Copy To dir exist RecipeName='%s'", to_name)
  else:
    func_ret = set_recipe(to_name, n)
    # 2021/03/16 hato ------------------------------ start ------------------------------
    #commands.getoutput('cp -a '
    #                   + dirpath + '/' + from_name + ' '
    #                   + dirpath + '/' + to_name)
    subprocess.getoutput('cp -a '
                       + dirpath + '/' + from_name + ' '
                       + dirpath + '/' + to_name)
    # 2021/03/16 hato ------------------------------  end  ------------------------------
    massage = (exec_item["name"] + ' ' + MSG_TBL["ok"] + '\n'
               + 'From:' + from_name + '\n'
               + 'To:' + to_name)
    rospy.loginfo("Recipe:copy RecipeName from='%s' to='%s'", from_name, to_name)
  return func_ret

def cb_open_dir(n):
  global massage
  func_ret = False
  name = buttons[n]["name"]
  ret = askopendirname(parent=root,
                       title=name,
                       initialdir=dirpath,
                       initialfile='',
                       okbuttontext=name)
  if ret:
    abs_path = os.path.abspath(Config["dump_prefix"])
    if ret.startswith(abs_path):
      dir = re.sub(r'.*'+Config["dump_prefix"], '', ret)
      recipe = dir.split('/')
      if (len(recipe) == 2) and (not recipe[0]):
        func_ret = set_recipe(recipe[1], n)
        if name == 'CopySelect':
          cb_copy_from()
      else:
        massage = name + ' Wrong selection folder'
    else:
      massage = name + ' Wrong selection folder'
  return func_ret

def cb_save_as(n):
  global massage
  func_ret = False
  name = buttons[n]["name"]
  ret = asksaveasfilename(parent=root,
                          title=name,
                          defaultext='',
                          initialdir=dirpath,
                          initialfile='',
                          filetypes=[('Directory', '*/')],
                          okbuttontext='Ok')
  if ret:
    recipe = ret.split('/')
    if recipe[-1]:
      func_ret = set_recipe(recipe[-1], n)
    else:
      massage = name + ' RecipeName Empty'
  return func_ret

def cb_default_recipe(n):
  func_ret = set_recipe('', n)
  return func_ret

def cb_button(n):
  global massage, is_exec
  is_exec = True
  set_button_enable(False)
  massage = ''
  result = False
  func = buttons[n]["func"]
  if func == 'open':
    result = cb_open_dir(n)
  elif func == 'save':
    result = cb_save_as(n)
  elif func == 'default':
    result = cb_default_recipe(n)
  elif func == 'copy':
    result = cb_copy(n)
  if massage:
    if result:
      f = tkMessageBox.showinfo('Notification', massage, parent=root)
    else:
      f = tkMessageBox.showerror('Warning', massage, parent=root)
  flg = not check_edit_mode()
  set_button_enable(flg)
  is_exec = False

def cb_button_enable(enable):
  set_button_enable(enable)

def cb_button_normal():
  global statcheck
  statcheck = 0
  if check_button_chenge(True):
    set_button_enable(True)

def cb_edit_stat(msg):
  global statcheck
  flg = not msg.data
  if statcheck:
    timeout.clear(statcheck)
    statcheck = 0
  if msg.data:
    if "stat_timeout" in Config:
      statcheck = timeout.set(cb_button_normal, Config["stat_timeout"])
  if check_button_chenge(flg):
    timeout.set(functools.partial(cb_button_enable, flg), 0)

def check_button_chenge(enable):
  ret = ((not is_exec) and (is_enable != enable))
  return ret

def check_edit_mode():
  try:
    val = rospy.get_param('~mode')
  except Exception:
    val = 0
  ret = (val == 1)
  return ret

def set_button_enable(enable):
  global is_enable
  for item in buttons:
    if "button" in item:
      if enable:
        item["button"]['state'] = tk.NORMAL
      else:
        item["button"]['state'] = tk.DISABLED
  is_enable = enable

def cb_do_nothing():
  pass

################
def parse_argv(argv):
  args = {}
  for arg in argv:
    tokens = arg.split(':=')
    if len(tokens) == 2:
      key = tokens[0]
      if re.match(r'\([ ]*([0-9.]+,[ ]*)*[0-9.]+[ ]*\)$',tokens[1]):
        # convert tuple-like-string to tuple
        args[key] = eval(tokens[1])
        continue
      args[key] = tokens[1]
  return args
####ROS Init####
rospy.init_node("recipe",anonymous=True)
try:
  conf = rospy.get_param("/config/recipe")
except:
  conf = {}
try:
  dictlib.merge(Config,conf)
except Exception as e:
  print("get_param exception:",e.args)

dictlib.merge(Config,parse_argv(sys.argv))

dirpath = Config["dump_prefix"]
# 2021/03/16 hato ------------------------------ start ------------------------------
# thispath = commands.getoutput("rospack find rtk_tools")
thispath = subprocess.getoutput("rospack find rtk_tools")
# 2021/03/16 hato ------------------------------ start ------------------------------

buttons = []
entrys = dict()
exec_item = dict()
pubs_tbl = dict()
MSG_TBL = {
  "ok": "Finished",
  "ng": "failed",
  "timeout": "no reply"
}
massage = ''
recipe_name = ''
is_exec = False
is_enable = True
statcheck = 0

####Bools
mTrue = Bool()
mTrue.data = True
mFalse = Bool()

####sub pub
pub_x0 = rospy.Publisher('~clear',Bool, queue_size=1)

####Layout####
font = (Config["font"]["family"], Config["font"]["size"], "normal")
btcolor = Config["color"]["button"]

root = tk.Tk()
root.title("Recipe")
root.geometry(str(Config["geom"]))
root.attributes('-topmost', True)
root.resizable(0, 0)
root.protocol('WM_DELETE_WINDOW', cb_do_nothing)

frame = tk.Frame(root, bd=2)
frame.grid(sticky='ne'+'nw'+'s',padx=(5, 5), pady=(5, 5))

####ICONS####
iconpath = thispath + "/icon/"

# p_topic topic_type is String type and Recipe Name only
# p_next  publishe topic '~clear'
# s_topic topic_type is Bool and False only
f = open(Config["panel_conf"], 'r')
lines = f.readlines()
row_no = -1
for n, line in enumerate(lines):
  try:
    prop = eval("{"+line+"}")
  except:
    continue
  if "class" not in prop:
    continue
  if "row" in prop:
    row_no += 1
  if row_no < 0:
    row_no = 0
  col_no = 0
  if "col" in prop:
    col_no = int(prop["col"])
  if prop["class"] == 'Button':
    item={}
    n = len(buttons)
    item = prop
    if "p_topic" in prop:
      if prop["p_topic"] not in pubs_tbl:
        pubs_tbl[prop["p_topic"]] = rospy.Publisher(prop["p_topic"],
                                                    String, queue_size=1)
      item["pub"] = pubs_tbl[prop["p_topic"]]
    if "icon" in prop:
      icon = tk.PhotoImage(file=iconpath+prop["icon"])
      item["button"] = tk.Button(frame, image=icon,
                                 bd=0, background=btcolor,
                                 highlightthickness=0,
                                 command=functools.partial(cb_button, n))
      item["button"].grid(column=col_no, row=row_no,
                          sticky='ne'+'nw'+'s',
                          padx=(0, 5), pady=(0, 5))
    else:
      item["button"] = tk.Button(frame, text=prop["name"],
                                 bd=0, background=btcolor,
                                 highlightthickness=0,
                                 command=functools.partial(cb_button, n))
      item["button"].grid(column=col_no, row=row_no,
                          sticky='ne'+'nw'+'s',
                          padx=(0, 5), pady=(0, 5), ipady=5)
    print("recipe item ", n, item)
    buttons.append(item)
  elif prop["class"] == 'Label':
    wlabel = tk.Label(frame, text=(prop["name"]+':'),
                      font=font)
    wlabel.grid(column=col_no, row=row_no,
                sticky='ne'+'nw'+'s',
                padx=(0, 5), pady=(0, 5), ipady=5)
  elif prop["class"] == 'Entry':
    entrys[prop["name"]] = tk.Entry(frame, font=font, width=20)
    entrys[prop["name"]].grid(column=col_no, row=row_no,
                              sticky='ne'+'nw'+'s',
                              padx=(0, 5), pady=(0, 5), ipady=5)
    entrys[prop["name"]].insert(0, '')
f.close()

flg = not check_edit_mode()
set_button_enable(flg)
rospy.Subscriber('~stat', Bool, cb_edit_stat)

while not rospy.is_shutdown():
  timeout.update()
  try:
    root.update()
  except Exception as e:
    print("recipe update exception", e.args)
    sys.exit(0)
  time.sleep(1)
