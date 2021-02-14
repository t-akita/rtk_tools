import tkinter as tk
import tkinter.ttk
import time

class dashLog:
  def __init__(self,pos,wid,fg,bg):
    self.buffer=[]
    self.box=None
    self.text=None
    self.pos=pos
    self.wid=wid
    self.fg=fg
    self.bg=bg
    self.hys=50
  def close(self):
    self.box.destroy()
    self.box=None
  def popup(self):
    if self.box is not None: return
    self.box=tk.Tk()
    self.box.geometry(self.pos)
    self.box.protocol("WM_DELETE_WINDOW",self.close)
    self.text=tk.Text(self.box,width=self.wid,height=20,foreground=self.fg,background=self.bg)
    self.text.pack(side='left',fill='y',anchor='nw')
    msg=""
    for ln in self.buffer:
      msg=msg+ln+"\n"
    self.text.insert("1.0",msg)
    self.text.delete(str(self.hys)+".0",tk.END)
  def push(self,msg):
    t=time.time()
    s="["+str(t)+"] "+msg.data
    self.buffer.insert(0,s)
    if len(self.buffer)>self.hys: self.buffer.pop()
    if self.box is not None:
      self.text.insert("1.0",s+"\n")
      self.text.delete(str(self.hys)+".0",tk.END)
