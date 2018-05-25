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
photoDir = '/home/egcs/BatteryIMG/'
topcam = Camera('top')
log.debug('TopCam Object:' + str(topcam))
bottomcam = Camera('bottom')
log.debug('BottomCam Object:' + str(bottomcam))

def takePhoto(position, photoID = 'None'):
    global topcam
    global bottomcam
    ts = time.strftime('%Y%m%d%H%M%S') #time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    photoloc = photoDir + ts + position + '.bmp'
    camera = topcam if position == 'top' else bottomcam
    PVRes = PVTopRes if position == 'top' else PVBottomRes

    img = camera.takephoto(photoloc)
    if img == -1:
        log.error(position + ' Camera Error!')
    else:
        PVCamStat.put(position.upper() + 'PHOTOED', wait = True)
        log.info("Camera Status: " + PVCamStat.get())
        results = detectFlaws(img)
        log.debug("Flaw detect Algorithm complete!")
        if results != 'null':
            PVRes.put('Bad', wait = True)
            threading.Thread(camera.saveImgFile(photoloc, results)).start()
        else:
            PVRes.put('Good', wait = True)

        log.info(photoID + position + ' Result is: ' +  'Bad!' if results != 'null' else 'Good!')


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
    PVTopRes = epics.PV("LQ:ROBOT:DRI:check_top")
    PVBottomRes = epics.PV("LQ:ROBOT:DRI:check_bottom")
    PVCamStat = epics.PV("LQ:CAMERA:DRI:cam_stat")
    PVctrlcmd = epics.PV("LQ:CAMERA:DRI:ctrl_cmd")
    PVproductID = epics.PV("LQ:ROBOT:soft:product_ID")
    PVctrlcmd.add_callback(ctrlCommand)
    running = True
    log.info('Ready for taking photo...')
    productID = ''
    while running:
        while not cmdQueue.empty():
            cmd = cmdQueue.get()
            log.info("Photo command: " + cmd)
            if cmd != 'EXIT':
                if cmd[5:] == 'top':
                    #while productID != PVproductID.get():
                    #log.error("Waiting for product " + productID + ' Bottom photo...')
                    #time.sleep(1)
                    threading.Thread(target = takePhoto, args = ('top', productID)).start()
                elif cmd[5:] == 'bottom':
                    if PVproductID.get() != 'NULL':
                        log.info('------------------------------------Product ' + productID + ' checking flow complete!------------------------------------')
                        productID = 'B' + time.strftime('%Y%m%d%H%M%S')
                        PVproductID.put(productID)
                        log.info('------------------------------------Product ' + productID + ' checking flow start!------------------------------------')
                        threading.Thread(target = takePhoto, args = ('bottom', productID)).start()
                else:
                    None

                log.info('Waiting For Photo Command...')
            else:
                running = False
    
    topcam.close()
    bottomcam.close()
