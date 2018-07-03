'''
Created on Apr 24, 2018

@author: qiuyx
'''
import epics, time, threading
from Queue import Queue
from DahuaCam.camera import Camera
from FlawDetect.thrift_client import detectFlaws
from ControlUtils.LeqiLogger import logger

log = logger('camera','/opt/BatteryFlawDetector/logs/debug.log')
cnt = 0
cmdQueue = Queue()
photoDir = '/home/egcs/BatteryIMG'
camset = {'VTop' : Camera('VTop'), 'STop' : Camera('STop'), 'VBottom' : Camera('VBottom'), 'SBottom' : Camera('SBottom')}
log.debug('Vertical TopCam Object:' + str(camset['VTop']))
log.debug('Slant TopCam Object:' + str(camset['STop']))
log.debug('Vertical BottomCam Object:' + str(camset['VBottom']))
log.debug('TopCam Object:' + str(camset['SBottom']))


def takePhoto(position, productID):
    global camset
    PVResults = {'VTop' : PVVTopRes, 'STop' : PVSTopRes, 'VBottom': PVVBottomRes, 'SBottom':PVSBottomRes}
    PVCamsStat = {'VTop' : PVVTopCamStat, 'STop' : PVSTopCamStat, 'VBottom': PVVBottomCamStat, 'SBottom' : PVSBottomCamStat}
    camera, PVRes, PVStat = camset[position], PVResults[position], PVCamsStat[position]
    

    camera.takephoto()
    if camera.stat == 'ERROR':
        log.error(position + ' Camera Error!')
    else:
        PVStat.put(position.upper() + 'PHOTOED', wait = True)
        log.info("Camera Status: " + PVStat.get())
        results = detectFlaws(camera.imgcontent)
        log.debug("Flaw detect Algorithm complete!")
        if results != 'null':
            PVRes.put('Bad', wait = True)
        else:
            PVRes.put('Good', wait = True)

        threading.Thread(camera.saveImgFile(photoDir, productID, results)).start()
        log.info(productID + position + ' Result is: ' +  'Bad!' if results != 'null' else 'Good!')


def ctrlCommand(pvname = None, value = None, char_value = None, **kw):
    global cnt
    global cmdQueue
    if cnt > 0:
        if char_value != 'NULL':
            cmdQueue.put(char_value)
        else:
            log.info("Camera PV connected.")

    cnt += 1


if __name__ == "__main__":

    #PVs:
    PVVTopRes = epics.PV("LQ:ROBOT:DRI:check_VTop")
    PVSTopRes = epics.PV("LQ:ROBOT:DRI:check_STop")
    PVVBottomRes = epics.PV("LQ:ROBOT:DRI:check_VBottom")
    PVSBottomRes = epics.PV("LQ:ROBOT:DRI:check_SBottom")

    PVVTopCamStat = epics.PV("LQ:CAMERA:DRI:camVTop_stat")
    PVSTopCamStat = epics.PV("LQ:CAMERA:DRI:camSTop_stat")
    PVVBottomCamStat = epics.PV("LQ:CAMERA:DRI:camVBottom_stat")
    PVSBottomCamStat = epics.PV("LQ:CAMERA:DRI:camSBottom_stat")

    PVctrlcmd = epics.PV("LQ:CAMERA:DRI:ctrl_cmd")
    PVproductID = epics.PV("LQ:ROBOT:soft:product_ID")
    PVctrlcmd.add_callback(ctrlCommand)
    running = True
    log.info('Ready for taking photo...')
    while running:
        while not cmdQueue.empty():
            cmd = cmdQueue.get()
            log.info("Photo command :" + cmd)
            if cmd != 'EXIT':
                if cmd[5:] == 'top':
                    #while productID != PVproductID.get():
                    #log.error("Waiting for product " + productID + ' Bottom photo...')
                    #time.sleep(1)
                    threading.Thread(target = takePhoto, args = ('VTop', PVproductID.get())).start()
                    time.sleep(0.3)
                    threading.Thread(target = takePhoto, args = ('STop', PVproductID.get())).start()
                elif cmd[5:] == 'bottom':
                    #if PVproductID.get() != 'NULL':
                    log.info('------------------------------------Product ' + PVproductID.get() + ' checking flow complete!------------------------------------')
                    productID = 'B' + time.strftime('%Y%m%d%H%M%S')
                    PVproductID.put(productID, wait = True)
                    log.info('------------------------------------Product ' + PVproductID.get() + ' checking flow start!------------------------------------')
                    VBottomCam = threading.Thread(target = takePhoto, args = ('VBottom', PVproductID.get()))
                    VBottomCam.start()
                    time.sleep(0.08)
                    SBottomCam = threading.Thread(target = takePhoto, args = ('SBottom', PVproductID.get()))
                    SBottomCam.start()
                else:
                    None

                log.info('Waiting For Photo Command...')
            else:
                running = False
    
    for cam in camset.values():
        cam.close()
