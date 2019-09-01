
import network
import socket
import time
import binascii
from machine import Pin,Timer,PWM
class Inj(object):
  wlan=None
  listenSocket=None
  rpm=PWM(Pin(2))
  drain=Pin(4,Pin.OUT)
  fuelpump=PWM(Pin(5))
  ultrasonic=Pin(18,Pin.OUT)
  detik=0
  menit=0
  timer=Timer(0)
  status=0
  start=0
  data_masuk="0000000000000000"
  def __init__(self,*args,**kwargs):
    super(Inj,self).__init__(**kwargs)
    self.timer.init(period=1000,callback=self.cb)
    self.rpm.freq(0)
    self.rpm.duty(0)
    self.fuelpump.freq(0)
    self.fuelpump.duty(0)
    
    self.drain.value(0)
    
    
    self.connect()
    
  def connect(self):
    self.wlan=network.WLAN(network.AP_IF)         #create a wlan object
    self.wlan.active(True)                         #Activate the network interface
    self.wlan.config(essid="injector tester")
    while(self.wlan.ifconfig()[0]=='0.0.0.0'):
      time.sleep(1)
    try:
      ip=self.wlan.ifconfig()[0]                     #get ip addr
      self.listenSocket = socket.socket()            #create socket
      self.listenSocket.bind((ip,800))              #bind ip and port
      self.listenSocket.listen(1)                    #listen message
      self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    #Set the value of the given socket option
      print ('tcp waiting...')
      while True:
        print("accepting.....")
        conn,addr = self.listenSocket.accept()       #Accept a connection,conn is a new socket object
        print(addr,"connected")
        while True:
          data = conn.recv(16)                #Receive 1024 byte of data from the socket
          if(len(data) == 0):
            print("close socket")
            conn.close()                        #if there is no data,close
            break
          
          self.data_masuk=data.decode()
          print(self.data_masuk)
          conn.send(data)       

          ar=binascii.unhexlify(self.data_masuk)
          rpm=int(ar[4]/0.6)
          self.start=ar[0]
          drain=ar[1]
          self.menit=ar[2]
          self.detik=ar[3]
          duty_c=ar[5]
          fuelpump=ar[6]
          ultrasonic=ar[7]
          self.drain.value(drain)
          self.ultrasonic.value(ultrasonic)
          if self.start==1:
            self.rpm.freq(rpm)
            self.rpm.duty(int(duty_c/100*rpm))
            self.fuelpump.freq(100)
            self.fuelpump.duty(fuelpump)
            self.timer.init(period=1000,callback=self.cb)
          else:
            self.rpm.freq(0)
            self.rpm.duty(0)
            self.fuelpump.freq(0)
            self.fuelpump.duty(0)
    except:
      if(self.listenSocket):
        self.listenSocket.close()
      self.wlan.active(False)
  def cb(self,dt):
    print("timer_start")
    if self.start==1:
      
      self.detik-=1
      if self.detik==-1:
        self.menit-=1
        self.detik=59
        
      if self.menit==-1:
        self.rpm.freq(0)
        self.rpm.duty(0)
        self.fuelpump.freq(0)
        self.fuelpump.duty(0)
        self.timer.deinit()
        self.detik=0
        self.menit=0
        self.timer.deinit()
        print("start 0")
      print(self.menit,self.detik)
   



Inj()
