# -*- coding: utf-8 -*-
import requests
import json
import binascii
import nfc
import time
from threading import Thread, Timer
import ConfigParser

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("hoge")

inifile = ConfigParser.SafeConfigParser()
inifile.read('./config.ini')

dry_run = False

# login CANDY HOUSE account and get token
token = inifile.get('credentials', 'token')
device_id = inifile.get('settings', 'device_id')

# Suica待ち受けの1サイクル秒
TIME_cycle = 1.0
# Suica待ち受けの反応インターバル秒
TIME_interval = 0.2
# タッチされてから次の待ち受けを開始するまで無効化する秒
TIME_wait = 3

# NFC接続リクエストのための準備
# 212F(FeliCa)で設定
target_req_suica = nfc.clf.RemoteTarget("212F")
# 0003(Suica)
target_req_suica.sensf_req = bytearray.fromhex("0000030000")

print 'Waiting for SUICA...'
while True:
    # USBに接続されたNFCリーダに接続してインスタンス化
    clf = nfc.ContactlessFrontend('usb')
    # Suica待ち受け開始
    # clf.sense( [リモートターゲット], [検索回数], [検索の間隔] )
    target_res = clf.sense(target_req_suica, iterations=int(TIME_cycle//TIME_interval)+1 , interval=TIME_interval)
    
    if target_res != None:
        
        #tag = nfc.tag.tt3.Type3Tag(clf, target_res)
        #なんか仕様変わったっぽい？↓なら動いた
        tag = nfc.tag.activate_tt3(clf, target_res)
        tag.sys = 3
        
        #IDmを取り出す
        idm = binascii.hexlify(tag.idm)
        print 'Suica detected. idm = ' + idm
        
        if (idm == "0139bcfc0597e6f5") or (idm == "0139e9876547e6f5") or (idm == "01010a1234567100"): #Jerming Watch or Mako iPhone7 or Yui PASMO
            if dry_run:
            	print("matched " + idm)
            else:

            	# unlock Sesame with token
            	url_control = "https://api.candyhouse.co/public/sesame/" + device_id
            	head_control = {"Authorization": token, "Content-type": "application/json"}
            	payload_control = {"command":"unlock"}
            	response_control = requests.post(url_control, headers=head_control, data=json.dumps(payload_control))
            
            	print(response_control.text)
        
        print 'sleep ' + str(TIME_wait) + ' seconds'
        time.sleep(TIME_wait)
    #end if
    
    clf.close()

#end while
 
