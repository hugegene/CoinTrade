# import threading
import sys
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor 
# telegram Library
import telegram
from functools import partial, wraps
import time
import queue

class TooSoon(Exception):
  """Can't be called so soon"""
  pass

class CoolDownDecorator(object):
  def __init__(self,func,interval):
    self.func = func
    self.interval = interval
    self.last_run = 0
  def __get__(self,obj,objtype=None):
    if obj is None:
      return self.func
    return partial(self,obj)
  def __call__(self,*args,**kwargs):
    now = time.time()
    if now - self.last_run < self.interval:
      raise TooSoon("Exception Handled: telegram alert can only can be called after {0} seconds".format(self.last_run + self.interval - now))
    else:
      self.last_run = now
      return self.func(*args,**kwargs)

def CoolDown(interval):
  def applyDecorator(func):
    decorator = CoolDownDecorator(func=func,interval=interval)
    return wraps(func)(decorator)
  return applyDecorator

tp = ThreadPoolExecutor(1)
def threaded(fn):
    def wrapper(*args, **kwargs):
        return tp.submit(fn, *args, **kwargs)  # returns Future object
    return wrapper

class teleBot() :
    
    def __init__(self,bucket,chat_id,token) :
        super(teleBot, self).__init__()
        print('teleBot Class created')
        try:
            self.bucket = bucket
            self.chat_id = chat_id
            self.chatList = self.chat_id.split(',')
            self.token = token
            self.bot = telegram.Bot(token=self.token)
            self.bio = BytesIO()
            self.bio.name = 'image.jpeg'
            self.msg = ''
            self.imgPath = ''
            self.imgType = ''
        except:
            raise Exception('Error Initialisze teleBot.')

    def run(self):
#         print('Run teleBot')
        try:
            self.sendTelegram()
            self.sendImg()
        except:
            print('Error in teleBot run.')
            self.bucket.put(sys.exc_info())
    
    def setTextnImg(self,msg,img,imgType="File"):
        try:
            self.imgType = imgType
            self.msg = msg

            if imgType == "File":
                self.imgPath = img
            elif imgType == "Memory":
                img.save(self.bio, 'JPEG')
                self.bio.seek(0)
        except:
            print('Error in teleBot setTextnImg.')
            self.bucket.put(sys.exc_info())                
    
    
    def tryTeleAlert(self, msg, img):
        try:
            self.teleAlert(msg, img)
#             thread = threading.Thread(target = self.teleAlert, args=(msg, img))
#             thread.start()
#             return thread
        except Exception as e:
            print(e)
    
    @CoolDown(300)
    @threaded
    def teleAlert(self, msg, img, imgType="Memory"):
        try:
            self.bio = BytesIO()
            print("sending telegram alert")
            self.imgType = imgType
            self.msg = msg

            if imgType == "File":
                self.imgPath = img
            elif imgType == "Memory":
                img.save(self.bio, 'JPEG')
                self.bio.seek(0)
        except:
            print('Error in teleBot setTextnImg.')
            self.bucket.put(sys.exc_info())         
    
        try:
            self.sendTelegram()
            self.sendImg()
        except:
            print('Error in teleBot run.')
            self.bucket.put(sys.exc_info())
            
        try:
            exc = self.bucket.get(block=False)
        except queue.Empty:
            pass
        else:
            exc_type, exc_obj, exc_trace = exc
            logger.error('Error Sending TeleBot Message. Error: ' + str(exc_obj), exc_info=True)

    
    def sendTelegram(self):
        if len(self.msg) > 0:
#             print(self.msg)
            for chatID in self.chatList:
                self.bot.sendMessage(chat_id=chatID, text=self.msg)
#             self.bot.sendMessage(chat_id=self.chat_id, text=self.msg)
        
    def sendImg(self):
        if self.imgType == "File":
            for chatID in self.chatList:
                self.bot.send_photo(chat_id=chatID, photo=open(self.imgPath, 'rb'), timeout=100)
#             self.bot.send_photo(chat_id=self.chat_id, photo=open(self.imgPath, 'rb'), timeout=100)
        elif self.imgType == "Memory":
            for chatID in self.chatList:
                self.bio.seek(0)
                self.bot.send_photo(chat_id=chatID, photo=self.bio, timeout=100)
#             self.bot.send_photo(chat_id=self.chat_id, photo=self.bio, timeout=100)
        
#     def sendTelegram(self, msg):
#         self.bot.sendMessage(chat_id=self.chat_id, text=msg)
        
#     def sendImg(self, img, imgType="File"):
#         if imgType == "File":
#             self.bot.send_photo(chat_id=self.chat_id, photo=open(img, 'rb'), timeout=100)
#         elif imgType == "Memory":
#             img.save(self.bio, 'JPEG')
#             self.bio.seek(0)
#             self.bot.send_photo(chat_id=self.chat_id, photo=self.bio, timeout=100)

    def __del__(self):
        print('teleBot Class deleted')