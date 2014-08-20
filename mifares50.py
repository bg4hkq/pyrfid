#-*- coding: utf-8 -*-

__author__ = 'Baoz'
__date__ = '14-01-04'
__version__ = '0.10'
__desc__ = 'RFID for Python lib'

import atexit,yaml
from time import sleep
import binascii


DEBUG=False

def get_config(key):
    cfg = yaml.load(file('pyrfid/config.yaml'))
    if key == 'dev':
        return cfg['devices'][cfg['using']]['device']
    if key == 'baudrate':
        return cfg['devices'][cfg['using']]['baudrate']


def Serial(*args,**kwargs):
    try:
        import serial,os
        if os.path.isfile(get_config('dev')):
            return True
    except Exception,e:
        if DEBUG:
			print e
    try :
        dev_inst = serial.Serial(port=get_config('dev'),baudrate=get_config('baudrate'))
        return dev_inst
    except serial.SerialException,e:
		if DEBUG:
			print u'串口实例化错误,__init__.py:L29\n',e

head = 'AA BB'
key = 'ff ff ff ff ff ff'

class mifares50(object):
    def __init__(self,dev_inst):
        self.dev = dev_inst
        print '==================='
        print u'>Card Proto: ISO14443A Mifare S50'
        print u'>Using %s(%s,8n1)' % (self.dev.port,self.dev.baudrate)
        print '==================='
    def build_msg(self,dev_number='00 00',command='',args=''):
        if args == '':
            dt = str(dev_number+' '+command)
        else:
            dt = str(dev_number+' '+command+' '+args)
        msg_len = dt.count(' ')+2
        msg_sum = 00 ^ int(dev_number[-2:])
        msg_sum = None
        for i in dt.split(' ')[1:]:
            if msg_sum == None :
                msg_sum = int(str(dt.split(' ')[0]),16) ^ int(str(i),16)
            msg_sum = int(str(i),16) ^ int(msg_sum)
        if 'aa' in args:
			if DEBUG:
				print 'Src:',args
            args = str(args).replace('aa','aa 00')
			if DEBUG:
				print 'Dst:',args
        if args == '':
            msg = '%s %02x 00 %s %s %02x' %(head,msg_len,dev_number,command,msg_sum)
        else:
            msg = '%s %02x 00 %s %s %s %02x' %(head,msg_len,dev_number,command,args,msg_sum)
        msg = binascii.b2a_hex(msg.replace(' ',''))
        return msg
    def decode(self,msg):
        import binascii
        return binascii.b2a_hex(msg)
    def beep(self,style):
        if style == 'init':
            msg = self.build_msg(command='06 01',args='05')
            self.send(msg)
        elif style == 'read':
            msg = self.build_msg(command='06 01',args='05')
            self.send(msg)
        elif style == 'write':
            msg = self.build_msg(command='06 01',args='05')
            self.send(msg)
    def send(self,msg):
        self.dev.write(msg.decode('hex').decode('hex'))
        ret=self.dev.read(4)
        iw = self.dev.inWaiting()
        ret += self.dev.read(iw)
        data = self.decode(ret)
        rt = {'status':data[16:18],
              'data':data[18:-2].replace('aa00','aa'),
              }
        return rt
    def init_com(self):
        msg = self.build_msg(command = '01 01',args='03')
        self.send(msg)
        self.beep('init')
        self.set_light(color='green')
        return '>Init com baudrate 03-19200'
    def init_dev(self):
        self.dev.send(self.build_msg(command = '02 01'))
        self.set_light(color='green')
    def get_dev_number(self):
        print 'get_dv_number'
        msg = self.build_msg(command = '03 01')
    def init_dev_number(self):
        pass
    def set_light(self,color):
        if color == 'red':
            msg = self.build_msg(command = '07 01', args='01')
        elif color == 'green':
            msg = self.build_msg(command = '07 01', args='02')
        elif color == 'yellow':
            msg = self.build_msg(command = '07 01', args='03')
        else:
            msg = self.build_msg(command = '07 01', args='00')
        self.send(msg)
    def set_sleep(self):
        pass
    def set_ant_status(self):
        pass
    def find_card(self):
        msg = self.build_msg(command = '01 02',args='26')
#         self.beep(style='read')
        ret = self.send(msg)
        return ret
    def ant_coll(self):
        msg = self.build_msg(command = '02 02')
        ret = self.send(msg)
        ret1 = self.dumpdata(ret['data'])
        return ret1
    def sel_card(self,sn):
        msg = self.build_msg(command='03 02', args=sn)
        ret = self.send(msg)
        return ret
    def auth(self,method='60',block='00'):
        args = method + ' ' + block + ' ' + key
        msg = self.build_msg(command='07 02', args=args)
        ret = self.send(msg)
        return ret
    def read(self,size='00'):
        msg = self.build_msg(command='08 02', args=size)
        ret = self.send(msg)
        return ret
    def write(self,block,data):
        args = block + ' ' + self.dumpdata(data)
        while len(args.replace(' ','')) < 33:
            args += ' FF'
        args = args.replace('  ',' ')
        msg = self.build_msg(command='09 02', args=args)
        self.send(msg)
    def init_wallet(self):
        pass
    def read_wallet(self):
        pass
    def decrement(self):
        pass
    def increment(self):
        pass
    def restore(self):
        pass
    def transfer(self):
        pass
    def dumpdata(self,data):
        ret = ''
        k = 0
        if len(data) == 2:
            return data+' '
        if len(data) % 2:
            data = data + '00'
        for i in range(len(data)/2):
            if k == len(data)-2:
                ret += data[k:k+2]
                k += 2
            else:
                ret += data[k:k+2]+' '
                k += 2
        return ret
    def read_coin(self):
        self.find_card()
        self.sel_card(sn=self.ant_coll())
        self.beep(style='read')
        self.auth(block='04')
        sn = self.read('04')
        mz = self.read('05')
        key = self.read('06')
        key['data'] = key['data'].replace('aa00','aa')
        return {'sn':sn['data'][0:8],
                'mz':mz['data'].split('ff')[0],
                'key':key['data'],
                }
    def write_coin(self,dt):
        sn = dt['sn']
        mz = dt['mz']
        key = dt['key']
        self.find_card()
        self.sel_card(sn=self.ant_coll())
        self.beep(style='write')
        ret = self.auth(block='04')
        if ret['status'] == '00':
            self.write(block='04',data=sn)
            self.write(block='05', data=mz+'ff')
            self.write(block='06', data=key)
            return True
        return False
