# coding:utf-8
# _Writen_By_Mr_: Corwin.Zhang
# _Create_Date_：'2018/2/1 14:50'
# _Company_：上海洪朴信息科技有限公司
"""
    Here is annotation.
"""

from __future__ import division
import json
import time
import logging
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from gen_py import DianchiVI

_timing = 1.5

class DianChiVIHandler:
    def __init__(self):
        pass

    def detectFlaws(self, imageName, imageData):
        with open(imageName, mode='wb') as f:
            f.write(imageData)
        flaws = [{'name': 'tudian', 'confidence': 0.9, 'bbox': [400, 1500, 600, 1700]},
                 {'name': 'aodian', 'confidence': 0.94, 'bbox': [1400, 500, 1600, 700]}]
        
        logging.info('sleep {} second for minic the algorithm'.format(_timing))
        time.sleep(_timing)
        rv = json.dumps(flaws)
        print(rv)
        return rv

    def testOnLine(self):
        print('testOnLine')
        return True


def main(timing=None):
    if timing:
        global _timing
        _timing = timing

    handler = DianChiVIHandler()
    processor = DianchiVI.Processor(handler)
    transport = TSocket.TServerSocket(host='0.0.0.0', port=7912)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    print('server running')
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server.serve()


if __name__ == '__main__':
    main()

