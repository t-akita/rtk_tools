import time

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
def set(cb,delay):
  global sto_time,sto_tarray,sto_farray
  t=time.time()+delay
  sto_tarray.append(t)
  sto_farray.append(cb)
  sto_reflesh()
  return t
def clear(t):
  if len(sto_tarray)>0:
    try:
      idx=sto_tarray.index(t)
    except:
      print("sto::clear id not found",t)
    else:
      sto_tarray.pop(idx)
      sto_farray.pop(idx)
      sto_reflesh()
def update():
  global sto_time,sto_tarray,sto_farray
  if sto_time>0:
    if time.time()>sto_time:
      try:
        idx=sto_tarray.index(sto_time)
      except:
        print("sto::update id not found",sto_time)
      else:
        cb=sto_farray[idx]
        sto_tarray.pop(idx)
        sto_farray.pop(idx)
        sto_reflesh()
        cb()

