'''
Created on Apr 24, 2018

@author: qiuyx
'''
import socket, epics
from Queue import Queue
from ControlUtils.LeqiLogger import logger


log = logger('RobotB','/opt/BatteryFlawDetector/logs/debug.log')
cnt = 0
cmdQueue = Queue()

def ctrlCommand(pvname = None, value = None, char_value = None, **kw):
    global cnt
    global cmdQueue
    if cnt > 0:
        if char_value != 'NULL':
            log.debug('[IOC Command queued]: ' + char_value)
            cmdQueue.put(char_value)
    else:
        log.info("PV connected.")

    cnt += 1
       

if __name__ == "__main__":
    #PVs:
    PVctrlcmd = epics.PV("LQ:ROBOTB:DRI:ctrl_cmd")
    PVconnstat = epics.PV("LQ:ROBOTB:DRI:conn_stat")
    PVRobotBStat = epics.PV("LQ:ROBOTB:DRI:robot_stat")
    PVTopRes = epics.PV("LQ:ROBOT:DRI:check_top")
    PVBottomRes = epics.PV("LQ:ROBOT:DRI:check_bottom")
    PVCheckRes = epics.PV("LQ:ROBOT:DRI:check_result")
    PVctrlcmd.add_callback(ctrlCommand)
    
    
    #Robot States:
    states = {'(INIT@RobotB:)':'INITIALIZED',
              '(CATH@battery:)':'CATCHED',
              'CHECK':'CHECKED',
              '(RELS@good_battery:)':'LEFT',
              '(RELS@bad_battery:1:)':'LEFT'
              }
    HOST, PORT, BUF_SIZE = '192.168.10.3', 5002, 2048
    
    sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    log.info("Robot B service start at " + HOST + str(PORT))
    sockServer.bind((HOST, PORT))
    sockServer.listen(1)
    
    connected = False
    running = True
    conn = None
    while running:
        try:
            log.info('Listening...')
            conn, address = sockServer.accept()
            #conn.settimeout(110)
            conn.setblocking(1)
            PVconnstat.put(1, wait = True)
            connected = True
            log.info('Connection' + repr(conn) +  'Request Accepted from :' + repr(address))
            while connected:
                try:
                    if not cmdQueue.empty():
                        cmd = cmdQueue.get()
                        log.debug("[System command]: " + cmd)
                        if cmd == 'EXIT':
                            running = False
                            connected = False
                            break
                        elif cmd == 'CHECK':
                            while PVTopRes.get() == 'NULL' or PVBottomRes.get() == 'NULL':
                                None
                            
                            log.info("Top Result:" + PVTopRes.get())
                            log.info("Bottom Result:" + PVBottomRes.get())
        
                            isgood = 1 if PVTopRes.get() == 'Good' and PVBottomRes.get() == 'Good' else 0
                            PVTopRes.put('NULL', wait = True)
                            PVBottomRes.put('NULL', wait = True)
                            if isgood:
                                PVCheckRes.put('Good', wait = True)
                            else:
                                PVCheckRes.put('Bad', wait = True)
        
                            PVRobotBStat.put(states['CHECK'], wait = True)	
                            log.info("RobotB status:" + PVRobotBStat.get())
                            log.info("Check Result:" +  PVCheckRes.get())
                        else:
                            sendcnt = conn.send(cmd)
                            log.debug("[Robot Command]: " + cmd)
                            res = conn.recv(BUF_SIZE)
                            log.debug("[Robot Command Return]: " + res)
                            if res:
                                PVRobotBStat.put(states[cmd], wait = True)
                            else:
                                log.error("Robot B " + cmd + "ERROR!")

                        #print time.strftime('%Y-%m-%d %H:%M:%S'), "[INFO] Top Result:", PVTopRes.get()
                        log.info("Top Result:" + PVTopRes.get())
                        log.info("Bottom Result:" + PVBottomRes.get())
                        log.info("Check Result:" + PVCheckRes.get())
                        log.info("RobotB stat:" + PVRobotBStat.get())
                        
                except socket.timeout:
                    log.error("Command Execution timeout!")
                    connected = False
                    PVconnstat.put(0, wait = True)
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                    
        except KeyboardInterrupt:
            log.info('KeyboardInterrupt')
            running = False
            connected = False
            PVconnstat.put(0, wait = True)
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            raise
            
        except Exception, e:
            running = False
            connected = False
            PVconnstat.put(0, wait = True)
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            log.error("Exception" + str(e) + 'Occurred!', exc_info = True)
            raise
    
    log.info('Task Finished!')
