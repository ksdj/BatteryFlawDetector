# coding:utf-8
import sys
import os
import random, cv2
import os.path as osp


from gen_py import DianchiVI


from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

_HOST = 'localhost'#'192.168.3.188' #
def test_testOnLine():
    transport = TSocket.TSocket(_HOST, 7912)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = DianchiVI.Client(protocol)

    # Connect!
    transport.open()


    rv = client.testOnLine()
    print(rv)

    # Close!
    transport.close()

def test_detectFlaws():
    transport = TSocket.TSocket(_HOST, 7912)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = DianchiVI.Client(protocol)

    # Connect!
    transport.open()

    #im = cv2.imagerd()
    with open('battery_01.jpg','rb') as img:
	content = img.read()
	if not content:
		print 'Photo read failed!'
	else:	
		rv = client.detectFlaws('battery_01.jpg', content)
    print(rv)

    # Close!
    transport.close()

def main():
    test_testOnLine()
    test_detectFlaws()

if __name__=='__main__':
    main()
