#-*- coding: utf-8 -*-

__author__ = 'Baoz'
__date__ = '14-01-04'
__version__ = '0.10'
__desc__ = 'RFID test'


from pyrfid import *
import binascii

m = mifares50(Serial())
print u'寻卡'
m.find_card()
print u'选卡'
print m.ant_coll()
m.sel_card(sn=m.ant_coll())
# print u'验证'
# m.auth(block='06')
# dt={
#     'sn':'10000000',
#     'mz':'50',
#     'key':'c5810223af6f0fc3c9b8f8c78c5df619',
#     }
# # m.write_coin(dt)
# # print m.read('04')
# m.write('06','e1f31e09bacf8b0252d421c8863241b4')
print m.read_coin()
