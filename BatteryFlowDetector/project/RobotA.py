'''
Created on Apr 24, 2018

@author: qiuyx
'''
import socket, epics
from Queue import Queue
from ControlUtils.LeqiLogger import logger


log = logger('RobotA','/opt/BatteryFlawDetector/logs/debug.log')
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
    PVctrlcmd = epics.PV("LQ:ROBOTA:DRI:ctrl_cmd")
    PVconnstat = epics.PV("LQ:ROBOTA:DRI:conn_stat")
    PVRobotAStat = epics.PV("LQ:ROBOTA:DRI:robot_stat")
    PVTopRes = epics.PV("LQ:ROBOT:DRI:check_top")
    PVBottomRes = epics.PV("LQ:ROBOT:DRI:check_bottom")
    PVctrlcmd.add_callback(ctrlCommand)
    
    
    #Robot States:
    states = {'(INIT@RobotA:)':'INITIALIZED'}
    
    
    HOST, PORT, BUF_SIZE = '192.168.10.3', 5001, 2048
    
    sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    log.info('Robot A service start at ' + HOST + str(PORT))
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
            log.info('Connection' + str(conn) + 'Request Accepted from :' + str(address))
            while connected:
                try:
                    if not cmdQueue.empty():
                        cmd = cmdQueue.get()
                        log.debug("[System command]: " + cmd)
                        if cmd == 'EXIT':
                            running = False
                            connected = False
                            break
                        elif cmd[1:5] == 'TAIL':
                            sendcnt = conn.send(cmd)
                            log.debug("[Robot Command]: " + cmd)
                            res = conn.recv(BUF_SIZE)
                            if res: #conn.recv(BUF_SIZE):
                                log.debug("[Robot Command Return]: " + res)
                                PVRobotAStat.put('RELEASED', wait = True)
                            else:
                                log.error("Releasing ERROR:")
                                running = False
                                connected = False
                                break

                            #tailed = conn.recv(BUF_SIZE)
                            res = conn.recv(BUF_SIZE)
                            if res: #conn.recv(BUF_SIZE):
                                log.debug("[Robot Command Return]: " + res)
                                PVRobotAStat.put('TAILED', wait = True)
                            else:
                                log.error("Tailing ERROR:")
                                running = False
                                connected = False
                                break
        
                            log.info("Tailing Complete!")
                            log.info(" RobotA stat:" + PVRobotAStat.get())
                        elif cmd[1:5] == 'INIT':
                            sendcnt = conn.send(cmd)
                            if conn.recv(BUF_SIZE):
                                PVRobotAStat.put(states[cmd], wait = True)
                                log.info("Initializing Sucessfully.")
                            else:
                                log.error("Initializing ERROR!")
                                running = False
                                connected = False

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
