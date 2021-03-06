#!/usr/bin/env python
# coding: utf-8
'''
Created on Apr 24, 2018

@author: qiuyx
'''
 
from ImageConvert import *
from MVSDK import *
from collections import deque
import struct, cv2, logging, json, subprocess, os, time, signal

logger = logging.getLogger('camera')
g_cameraStatusUserInfo = b"statusInfo"
camindexes = {'VTop' : 1, 'VBottom' : 2, 'STop' : 3, 'SBottom' : 0}

# 枚举相机
def enumCameras():
    # 获取系统单例
    system = pointer(GENICAM_System())
    nRet = GENICAM_getSystemInstance(byref(system))
    if ( nRet != 0 ):
        logger.error("getSystemInstance fail!")
        return None, None  

    # 发现相机 
    cameraList = pointer(GENICAM_Camera()) 
    cameraCnt = c_uint()
    nRet = system.contents.discovery(system, byref(cameraList), byref(cameraCnt), c_int(GENICAM_EProtocolType.typeAll));
    if ( nRet != 0 ):
        logger.error("discovery fail!")
        return None, None
    elif cameraCnt.value < 1:
        logger.error("discovery no camera!")
        return None, None
    else:
        logger.info("cameraCnt: " + str(cameraCnt.value))
        return cameraCnt.value, cameraList


cameraCnt, cameraList = enumCameras()


class BITMAPFILEHEADER(Structure):
    _fields_ = [
                ('bfType', c_ushort),
                ('bfSize', c_uint),
                ('bfReserved1', c_ushort),
                ('bfReserved2', c_ushort),
                ('bfOffBits', c_uint),
                ]
 
class BITMAPINFOHEADER(Structure):
    _fields_ = [
                ('biSize', c_uint),
                ('biWidth', c_int),
                ('biHeight', c_int),
                ('biPlanes', c_ushort),
                ('biBitCount', c_ushort),
                ('biCompression', c_uint),
                ('biSizeImage', c_uint),
                ('biXPelsPerMeter', c_int),
                ('biYPelsPerMeter', c_int),
                ('biClrUsed', c_uint),
                ('biClrImportant', c_uint),
                ] 

# 调色板，只有8bit及以下才需要
class RGBQUAD(Structure):
    _fields_ = [
                ('rgbBlue', c_ubyte),
                ('rgbGreen', c_ubyte),
                ('rgbRed', c_ubyte),
                ('rgbReserved', c_ubyte),
                ]

class Camera(object):
    def __init__(self, position):
        # 回调函数
        self.position = position
        self.logger = logging.getLogger('camera')
        self.__connectCallBackFuncEx = connectCallBackEx(self.deviceLinkNotify)
        self.__frameCallbackFunc = callbackFunc(self.onGetFrame)
        self.__frameCallbackFuncEx = callbackFuncEx(self.onGetFrameEx)
        self.imgcontent = None
        self.stat = 'IDLE'
        self.colortypes = {'aodian' : (27, 28, 240),
                      'tudian' : (41, 179, 18),
                      'zhezhou' : (255, 132, 0),
                      'guahen' : (39, 179, 255),
                      'qita' : (188, 67 ,125)}
        # 发现相机
        
        self.camera = cameraList[camindexes[position]]
        self.logger.info(str(cameraCnt) + " cameras connected!" + position + ' camera initializing!!!!!!')

        '''
        if cameraCnt != 2:
        print "Camera connected error!!!!!!!!!!!!!!"
            return -1
        '''

        # 显示相机信息
        self.showinfo()
        
        # 打开相机
        nRet = self.__openCamera()
        if ( nRet != 0 ):
            self.logger.error("openCamera fail.")
        
        # 相机初始化
        self.streamSource = self.prepare()

   
    def prepare(self):
        self.logger.debug('Creating ' + self.position + ' Camera Stream Object.')    
        # 创建流对象
        streamSourceInfo = GENICAM_StreamSourceInfo()
        streamSourceInfo.channelId = 0
        streamSourceInfo.pCamera = pointer(self.camera)

        streamSource = pointer(GENICAM_StreamSource())
        nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(streamSource))
        if ( nRet != 0 ):
            self.logger.error("create StreamSource fail!")
        
        # 设置软触发
        nRet = self.setSoftTriggerConf()
        if ( nRet != 0 ):
            self.logger.error("set SoftTriggerConf fail!")
            # 释放相关资源
            streamSource.contents.release(streamSource)
        else:
            self.logger.info("set SoftTriggerConf success!")
                        
        # 开始拉流
        nRet = streamSource.contents.startGrabbing(streamSource, c_ulonglong(0), c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
        if( nRet != 0 ):
            self.logger.error("startGrabbing fail!")
            # 释放相关资源
            streamSource.contents.release(streamSource)
        
        return streamSource

    def showinfo(self):
        
        info =  "\nCamera Id = " + str(self.camera) \
        + "Key           = " + str(self.camera.getKey(self.camera)) \
        + "vendor name   = " + str(self.camera.getVendorName(self.camera)) \
        + "Model  name   = " + str(self.camera.getModelName(self.camera)) \
        + "Serial number = " + str(self.camera.getSerialNumber(self.camera))

        return info


    # 取流回调函数                             
    def onGetFrame(self, frame):
        nRet = frame.contents.valid(frame)
        if ( nRet != 0):
            self.logger.error("frame is invalid!")
            # 释放驱动图像缓存资源
            frame.contents.release(frame)
            return    
        
        self.logger.info("BlockId = %d"  %(frame.contents.getBlockId(frame)))
        #此处客户应用程序应将图像拷贝出使用
        '''
        '''
        # 释放驱动图像缓存资源
        frame.contents.release(frame)


    # 取流回调函数Ex
    def onGetFrameEx(self, frame, userInfo):
        nRet = frame.contents.valid(frame)
        if ( nRet != 0):
            self.logger.error("frame is invalid!")
            # 释放驱动图像缓存资源
            frame.contents.release(frame)
            return         
     
        self.logger.info("BlockId = %d userInfo = %s"  %(frame.contents.getBlockId(frame), c_char_p(userInfo).value))
        #此处客户应用程序应将图像拷贝出使用
        '''
        '''
        # 释放驱动图像缓存资源
        frame.contents.release(frame)


    # 相机连接状态回调函数
    def deviceLinkNotify(self, connectArg, linkInfo):
        if ( EVType.offLine == connectArg.contents.m_event ):
            self.logger.info("camera has off line, userInfo [%s]" %(c_char_p(linkInfo).value))
        elif ( EVType.onLine == connectArg.contents.m_event ):
            self.logger.info("camera has on line, userInfo [%s]" %(c_char_p(linkInfo).value))
        
    
    # 注册相机连接状态回调
    def subscribeCameraStatus(self):
        # 注册上下线通知
        eventSubscribe = pointer(GENICAM_EventSubscribe())
        eventSubscribeInfo = GENICAM_EventSubscribeInfo()
        eventSubscribeInfo.pCamera = pointer(self.camera)
        nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
        if ( nRet != 0):
            self.logger.error("create eventSubscribe fail!")
            return -1
        
        nRet = eventSubscribe.contents.subscribeConnectArgsEx(eventSubscribe, self.__connectCallBackFuncEx, g_cameraStatusUserInfo)
        if ( nRet != 0 ):
            self.logger.error("subscribeConnectArgsEx fail!")
            # 释放相关资源
            eventSubscribe.contents.release(eventSubscribe)
            return -1  
        
        # 不再使用时，需释放相关资源
        eventSubscribe.contents.release(eventSubscribe) 
        return 0

    # 反注册相机连接状态回调
    def unsubscribeCameraStatus(self):
        # 反注册上下线通知
        eventSubscribe = pointer(GENICAM_EventSubscribe())
        eventSubscribeInfo = GENICAM_EventSubscribeInfo()
        eventSubscribeInfo.pCamera = pointer(self.camera)
        nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
        if ( nRet != 0):
            self.logger.error("create eventSubscribe fail!")
            return -1
            
        nRet = eventSubscribe.contents.unsubscribeConnectArgsEx(eventSubscribe, self.__connectCallBackFuncEx, g_cameraStatusUserInfo)
        if ( nRet != 0 ):
            self.logger.error("unsubscribeConnectArgsEx fail!")
            # 释放相关资源
            eventSubscribe.contents.release(eventSubscribe)
            return -1
        
        # 不再使用时，需释放相关资源
        eventSubscribe.contents.release(eventSubscribe)
        return 0   

    # 设置软触发
    def setSoftTriggerConf(self):
        # 创建control节点
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(self.camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(acqCtrl))
        if ( nRet != 0 ):
            self.logger.error("create AcquisitionControl fail!")
            return -1
        
        # 设置触发源为软触发
        trigSourceEnumNode = acqCtrl.contents.triggerSource(acqCtrl)
        nRet = trigSourceEnumNode.setValueBySymbol(byref(trigSourceEnumNode), b"Software")
        if ( nRet != 0 ):
            self.logger.error("set TriggerSource value [Software] fail!")
            # 释放相关资源
            trigSourceEnumNode.release(byref(trigSourceEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1
        
        # 需要释放Node资源
        trigSourceEnumNode.release(byref(trigSourceEnumNode))
        
        # 设置触发方式
        trigSelectorEnumNode = acqCtrl.contents.triggerSelector(acqCtrl)
        nRet = trigSelectorEnumNode.setValueBySymbol(byref(trigSelectorEnumNode), b"FrameStart")
        if ( nRet != 0 ):
            self.logger.error("set TriggerSelector value [FrameStart] fail!")
            # 释放相关资源
            trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
            acqCtrl.contents.release(acqCtrl) 
            return -1
         
        # 需要释放Node资源    
        trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
        
        # 打开触发模式
        trigModeEnumNode = acqCtrl.contents.triggerMode(acqCtrl)
        nRet = trigModeEnumNode.setValueBySymbol(byref(trigModeEnumNode), b"On")
        if ( nRet != 0 ):
            self.logger.error("set TriggerMode value [On] fail!")
            # 释放相关资源
            trigModeEnumNode.release(byref(trigModeEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1
        
        # 需要释放相关资源    
        trigModeEnumNode.release(byref(trigModeEnumNode))
        acqCtrl.contents.release(acqCtrl)
        
        return 0     
    
    # 设置外触发
    def setLineTriggerConf(self):
        # 创建control节点
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(self.camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(acqCtrl))
        if ( nRet != 0 ):
            self.logger.error("create AcquisitionControl fail!")
            return -1
        
        # 设置触发源为软触发
        trigSourceEnumNode = acqCtrl.contents.triggerSource(acqCtrl)
        nRet = trigSourceEnumNode.setValueBySymbol(byref(trigSourceEnumNode), b"Line1")
        if ( nRet != 0 ):
            self.logger.error("set TriggerSource value [Line1] fail!")
            # 释放相关资源
            trigSourceEnumNode.release(byref(trigSourceEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1
        
        # 需要释放Node资源
        trigSourceEnumNode.release(byref(trigSourceEnumNode))
        
        # 设置触发方式
        trigSelectorEnumNode = acqCtrl.contents.triggerSelector(acqCtrl)
        nRet = trigSelectorEnumNode.setValueBySymbol(byref(trigSelectorEnumNode), b"FrameStart")
        if ( nRet != 0 ):
            self.logger.error("set TriggerSelector value [FrameStart] fail!")
            # 释放相关资源
            trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
            acqCtrl.contents.release(acqCtrl) 
            return -1
         
        # 需要释放Node资源    
        trigSelectorEnumNode.release(byref(trigSelectorEnumNode))
        
        # 打开触发模式
        trigModeEnumNode = acqCtrl.contents.triggerMode(acqCtrl)
        nRet = trigModeEnumNode.setValueBySymbol(byref(trigModeEnumNode), b"On")
        if ( nRet != 0 ):
            self.logger.error("set TriggerMode value [On] fail!")
            # 释放相关资源
            trigModeEnumNode.release(byref(trigModeEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1
        
        # 需要释放Node资源    
        trigModeEnumNode.release(byref(trigModeEnumNode))
        
        # 设置触发沿
        trigActivationEnumNode = acqCtrl.contents.triggerActivation(acqCtrl)
        nRet = trigActivationEnumNode.setValueBySymbol(byref(trigActivationEnumNode), b"RisingEdge")
        if ( nRet != 0 ):
            self.logger.error("set TriggerActivation value [RisingEdge] fail!")
            # 释放相关资源
            trigActivationEnumNode.release(byref(trigActivationEnumNode))
            acqCtrl.contents.release(acqCtrl)
            return -1
        
        # 需要释放Node资源    
        trigActivationEnumNode.release(byref(trigActivationEnumNode))
        acqCtrl.contents.release(acqCtrl)
        return 0 

    # 打开相机
    def __openCamera(self):
        # 连接相机
        nRet = self.camera.connect(self.camera, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
        if ( nRet != 0 ):
            self.logger.error("camera connect fail!")
            return -1
        else:
            self.logger.info("camera connect success.")
      
        # 注册相机连接状态回调
        nRet = self.subscribeCameraStatus()
        if ( nRet != 0 ):
            self.logger.error("subscribeCameraStatus fail!")
            return -1
    
        return 0

    # 关闭相机
    def __closeCamera(self):
        # 反注册相机连接状态回调
        nRet = self.unsubscribeCameraStatus()
        if ( nRet != 0 ):
            self.logger.error("unsubscribeCameraStatus fail!")
            return -1
      
        # 断开相机
        nRet = self.camera.disConnect(byref(self.camera))
        if ( nRet != 0 ):
            self.logger.error("disConnect camera fail!")
            return -1
        
        return 0    

    # 设置曝光
    def setExposureTime(self, dVal):
        # 通用属性设置:设置曝光 --根据属性类型，直接构造属性节点。如曝光是 double类型，构造doubleNode节点
        exposureTimeNode = pointer(GENICAM_DoubleNode())
        exposureTimeNodeInfo = GENICAM_DoubleNodeInfo() 
        exposureTimeNodeInfo.pCamera = pointer(self.camera)
        exposureTimeNodeInfo.attrName = b"ExposureTime"
        nRet = GENICAM_createDoubleNode(byref(exposureTimeNodeInfo), byref(exposureTimeNode))
        if ( nRet != 0 ):
            self.logger.error("create ExposureTime Node fail!")
            return -1
          
        # 设置曝光时间
        nRet = exposureTimeNode.contents.setValue(exposureTimeNode, c_double(dVal))  
        if ( nRet != 0 ):
            self.logger.error("set ExposureTime value [%f]us fail!"  % (dVal))
            # 释放相关资源
            exposureTimeNode.contents.release(exposureTimeNode)
            return -1
        else:
            self.logger.info("set ExposureTime value [%f]us success." % (dVal))
                
        # 释放节点资源     
        exposureTimeNode.contents.release(exposureTimeNode)    
        return 0
        



    def grabOne(self):

        # 创建control节点
        acqCtrlInfo = GENICAM_AcquisitionControlInfo()
        acqCtrlInfo.pCamera = pointer(self.camera)
        acqCtrl = pointer(GENICAM_AcquisitionControl())
        nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(acqCtrl))
        if ( nRet != 0 ):
            self.logger.error("create AcquisitionControl fail!")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)  
            return -1
            
        # 执行一次软触发
        trigSoftwareCmdNode = acqCtrl.contents.triggerSoftware(acqCtrl)
        nRet = trigSoftwareCmdNode.execute(byref(trigSoftwareCmdNode))
        if( nRet != 0 ):
            self.logger.error("Execute triggerSoftware fail!")
            # 释放相关资源
            trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
            acqCtrl.contents.release(acqCtrl)
            self.streamSource.contents.release(self.streamSource)
            return -1   
    
        # 释放相关资源
        trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
        acqCtrl.contents.release(acqCtrl)
        #self.streamSource.contents.release(self.streamSource)
        return 0  


    # 设置感兴趣区域  --- 感兴趣区域的宽高 和 xy方向的偏移量  入参值应符合对应相机的递增规则
    def setROI(self, OffsetX, OffsetY, nWidth, nHeight):
        #获取原始的宽度
        widthMaxNode = pointer(GENICAM_IntNode())
        widthMaxNodeInfo = GENICAM_IntNodeInfo() 
        widthMaxNodeInfo.pCamera = pointer(self.camera)
        widthMaxNodeInfo.attrName = b"WidthMax"
        nRet = GENICAM_createIntNode(byref(widthMaxNodeInfo), byref(widthMaxNode))
        if ( nRet != 0 ):
            self.logger.error("create WidthMax Node fail!")
            return -1
        
        oriWidth = c_longlong()
        nRet = widthMaxNode.contents.getValue(widthMaxNode, byref(oriWidth))
        if ( nRet != 0 ):
            self.logger.error("widthMaxNode getValue fail!")
            # 释放相关资源
            widthMaxNode.contents.release(widthMaxNode)
            return -1  
        
        # 释放相关资源
        widthMaxNode.contents.release(widthMaxNode)
        
        # 获取原始的高度
        heightMaxNode = pointer(GENICAM_IntNode())
        heightMaxNodeInfo = GENICAM_IntNodeInfo() 
        heightMaxNodeInfo.pCamera = pointer(self.camera)
        heightMaxNodeInfo.attrName = b"HeightMax"
        nRet = GENICAM_createIntNode(byref(heightMaxNodeInfo), byref(heightMaxNode))
        if ( nRet != 0 ):
            self.logger.error("create HeightMax Node fail!")
            return -1
        
        oriHeight = c_longlong()
        nRet = heightMaxNode.contents.getValue(heightMaxNode, byref(oriHeight))
        if ( nRet != 0 ):
            self.logger.error("heightMaxNode getValue fail!")
            # 释放相关资源
            heightMaxNode.contents.release(heightMaxNode)
            return -1
        
        # 释放相关资源
        heightMaxNode.contents.release(heightMaxNode)
            
        # 检验参数
        if ( ( oriWidth.value < (OffsetX + nWidth)) or ( oriHeight.value < (OffsetY + nHeight)) ):
            self.logger.error("please check input param!")
            return -1
        
        # 设置宽度
        widthNode = pointer(GENICAM_IntNode())
        widthNodeInfo = GENICAM_IntNodeInfo() 
        widthNodeInfo.pCamera = pointer(self.camera)
        widthNodeInfo.attrName = b"Width"
        nRet = GENICAM_createIntNode(byref(widthNodeInfo), byref(widthNode))
        if ( nRet != 0 ):
            self.logger.error("create Width Node fail!") 
            return -1
        
        nRet = widthNode.contents.setValue(widthNode, c_longlong(nWidth))
        if ( nRet != 0 ):
            self.logger.error("widthNode setValue [%d] fail!" % (nWidth))
            # 释放相关资源
            widthNode.contents.release(widthNode)
            return -1  
        
        # 释放相关资源
        widthNode.contents.release(widthNode)
        
        # 设置高度
        heightNode = pointer(GENICAM_IntNode())
        heightNodeInfo = GENICAM_IntNodeInfo() 
        heightNodeInfo.pCamera = pointer(self.camera)
        heightNodeInfo.attrName = b"Height"
        nRet = GENICAM_createIntNode(byref(heightNodeInfo), byref(heightNode))
        if ( nRet != 0 ):
            self.logger.error("create Height Node fail!")
            return -1
        
        nRet = heightNode.contents.setValue(heightNode, c_longlong(nHeight))
        if ( nRet != 0 ):
            self.logger.error("heightNode setValue [%d] fail!" % (nHeight))
            # 释放相关资源
            heightNode.contents.release(heightNode)
            return -1    
        
        # 释放相关资源
        heightNode.contents.release(heightNode)    
        
        # 设置OffsetX
        OffsetXNode = pointer(GENICAM_IntNode())
        OffsetXNodeInfo = GENICAM_IntNodeInfo() 
        OffsetXNodeInfo.pCamera = pointer(self.camera)
        OffsetXNodeInfo.attrName = b"OffsetX"
        nRet = GENICAM_createIntNode(byref(OffsetXNodeInfo), byref(OffsetXNode))
        if ( nRet != 0 ):
            self.logger.error("create OffsetX Node fail!")
            return -1
        
        nRet = OffsetXNode.contents.setValue(OffsetXNode, c_longlong(OffsetX))
        if ( nRet != 0 ):
            self.logger.error("OffsetX setValue [%d] fail!" % (OffsetX))
            # 释放相关资源
            OffsetXNode.contents.release(OffsetXNode)
            return -1    
        
        # 释放相关资源
        OffsetXNode.contents.release(OffsetXNode)  
        
        # 设置OffsetY
        OffsetYNode = pointer(GENICAM_IntNode())
        OffsetYNodeInfo = GENICAM_IntNodeInfo() 
        OffsetYNodeInfo.pCamera = pointer(self.camera)
        OffsetYNodeInfo.attrName = b"OffsetY"
        nRet = GENICAM_createIntNode(byref(OffsetYNodeInfo), byref(OffsetYNode))
        if ( nRet != 0 ):
            self.logger.error("create OffsetY Node fail!")
            return -1
        
        nRet = OffsetYNode.contents.setValue(OffsetYNode, c_longlong(OffsetY))
        if ( nRet != 0 ):
            self.logger.error("OffsetY setValue [%d] fail!" % (OffsetY))
            # 释放相关资源
            OffsetYNode.contents.release(OffsetYNode)
            return -1    
        
        # 释放相关资源
        OffsetYNode.contents.release(OffsetYNode)   
        return 0

    def close(self):
        # 停止拉流
        nRet = self.streamSource.contents.stopGrabbing(self.streamSource)
        if( nRet != 0 ):
            self.logger.error("stopGrabbing fail!")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)   
            return -1
          
        # 设置曝光
        nRet = self.setExposureTime(20000)
        if ( nRet != 0 ):
            self.logger.error("set ExposureTime fail")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)   
            return -1
               
        # 关闭相机
        nRet = self.__closeCamera()
        if ( nRet != 0 ):
            self.logger.error("closeCamera fail")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)   
            return -1
         
        # 释放相关资源
        self.streamSource.contents.release(self.streamSource)
        return 0
        
    # Leqi Camera Call:
    def takephoto(self):
        #camera = cameraList[0]
        self.logger.info(str(self.camera) + 'is taking photo.')
    
        # 软触发取一张图
        nRet = self.grabOne()  
        if( nRet != 0 ):
            self.logger.info("grabOne fail!")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)   
            self.stat = 'ERROR'
            return      
        else:
            self.logger.debug("Trigger Timed! ")
        
        # 主动取图
        frame = pointer(GENICAM_Frame())
        nRet = self.streamSource.contents.getFrame(self.streamSource, byref(frame), c_uint(1000))
        if ( nRet != 0 ):
            self.logger.critical("----------------------------------------------------SoftTrigger getFrame fail! timeOut [1000]ms.--------------------------------")
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource) 
            self.stat = 'ERROR'
            return   
        else:
            self.logger.info("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame))) 
            self.logger.debug("get frame Timed! ")
          
        nRet = frame.contents.valid(frame)
        if ( nRet != 0 ):
            self.logger.error("frame is invalid!")
            # 释放驱动图像缓存资源
            frame.contents.release(frame)
            # 释放相关资源
            self.streamSource.contents.release(self.streamSource)
            self.stat = 'ERROR'
            return 
          
        # 将裸数据图像拷出
        imageSize = frame.contents.getImageSize(frame)
        buffAddr = frame.contents.getImage(frame)
        frameBuff = c_buffer(b'\0', imageSize)
        memmove(frameBuff, c_char_p(buffAddr), imageSize)
      
        # 将裸数据图像拷出
        # 给转码所需的参数赋值
        convertParams = IMGCNV_SOpenParam()
        convertParams.dataSize = imageSize
        convertParams.height = frame.contents.getImageHeight(frame)
        convertParams.width = frame.contents.getImageWidth(frame)
        convertParams.paddingX = frame.contents.getImagePaddingX(frame)
        convertParams.paddingY = frame.contents.getImagePaddingY(frame)
        convertParams.pixelForamt = frame.contents.getImagePixelFormat(frame)
          
        # 释放驱动图像缓存
        frame.contents.release(frame)
      
        # 保存bmp图片  
        bmpInfoHeader = BITMAPINFOHEADER() 
        bmpFileHeader = BITMAPFILEHEADER()
      
        uRgbQuadLen = 0
        rgbQuad = (RGBQUAD * 256)() # 调色板信息
        rgbBuff = c_buffer(b'\0', convertParams.height * convertParams.width * 3)
        
        # 如果图像格式是 Mono8 不需要转码 
        if convertParams.pixelForamt == EPixelType.gvspPixelMono8:
            # 初始化调色板rgbQuad 实际应用中 rgbQuad 只需初始化一次
            for i in range(0, 256):
                rgbQuad[i].rgbBlue = rgbQuad[i].rgbGreen = rgbQuad[i].rgbRed = i;
    
            uRgbQuadLen = sizeof(RGBQUAD) * 256    
            bmpFileHeader.bfSize = sizeof(bmpFileHeader) + sizeof(bmpInfoHeader) + uRgbQuadLen + convertParams.dataSize
            bmpInfoHeader.biBitCount = 8
        else:
            # 转码 => BGR24
            rgbSize = c_int()
            nRet = IMGCNV_ConvertToBGR24(cast(frameBuff, c_void_p), byref(convertParams), \
                                         cast(rgbBuff, c_void_p), byref(rgbSize))
          
            if ( nRet != 0 ):
                self.logger.error("image convert fail! errorCode = " + str(nRet))
                # 释放相关资源
                self.streamSource.contents.release(self.streamSource)
                self.stat = 'ERROR'
                return 
            
            bmpFileHeader.bfSize = sizeof(bmpFileHeader) + sizeof(bmpInfoHeader) + rgbSize.value
            bmpInfoHeader.biBitCount = 24   
        
        print '!!!!!!!!!!!!!!!!!!!!!!!!!'
        bmpFileHeader.bfType = 0x4D42 # 文件头类型 'BM'(42 4D)
        bmpFileHeader.bfReserved1 = 0 # 保留字
        bmpFileHeader.bfReserved2 = 0 # 保留字
        bmpFileHeader.bfOffBits = 54 + uRgbQuadLen # 位图像素数据的起始位置
          
        bmpInfoHeader.biSize = 40     # 信息头所占字节数
        bmpInfoHeader.biWidth = convertParams.width
        bmpInfoHeader.biHeight = -convertParams.height
        bmpInfoHeader.biPlanes = 1    # 位图平面数
        
        bmpInfoHeader.biCompression = 0  # 压缩类型，0 即不压缩
        bmpInfoHeader.biSizeImage = 0
        bmpInfoHeader.biXPelsPerMeter = 0
        bmpInfoHeader.biYPelsPerMeter = 0
        bmpInfoHeader.biClrUsed = 0
        bmpInfoHeader.biClrImportant = 0    

        imgcontent = ''
        content = deque()
        content.append(struct.pack('H', bmpFileHeader.bfType))
        content.append(struct.pack('I', bmpFileHeader.bfSize))
        content.append(struct.pack('H', bmpFileHeader.bfReserved1))
        content.append(struct.pack('H', bmpFileHeader.bfReserved2))
        content.append(struct.pack('I', bmpFileHeader.bfOffBits))
        content.append(struct.pack('I', bmpInfoHeader.biSize))
        content.append(struct.pack('i', bmpInfoHeader.biWidth))
        content.append(struct.pack('i', bmpInfoHeader.biHeight))
        content.append(struct.pack('H', bmpInfoHeader.biPlanes))
        content.append(struct.pack('H', bmpInfoHeader.biBitCount))
        content.append(struct.pack('I', bmpInfoHeader.biCompression))
        content.append(struct.pack('I', bmpInfoHeader.biSizeImage))
        content.append(struct.pack('i', bmpInfoHeader.biXPelsPerMeter))
        content.append(struct.pack('i', bmpInfoHeader.biYPelsPerMeter))
        content.append(struct.pack('I', bmpInfoHeader.biClrUsed))
        content.append(struct.pack('I', bmpInfoHeader.biClrImportant))
        
        
        self.logger.debug("Convert Header Info Timed! ")

        if convertParams.pixelForamt == EPixelType.gvspPixelMono8:
            # 写入调色板信息
            for i in range(0, 256):
                content.append(struct.pack('B', rgbQuad[i].rgbBlue))
                content.append(struct.pack('B', rgbQuad[i].rgbGreen))
                content.append(struct.pack('B', rgbQuad[i].rgbRed))
                content.append(struct.pack('B', rgbQuad[i].rgbReserved)) 
            self.logger.debug("Convert rgbQuad Timed! ")
            content.append(str(frameBuff.raw))
            
            self.logger.debug("Add frame Buff Timed!" +  str(type(frameBuff))) 
            imgcontent = imgcontent.join(content)
            self.logger.debug("Convert Frame Buff Timed! ")
        else:
            imgcontent = imgcontent.join(content) 
            imgcontent = imgcontent.join(rgbBuff)
            self.logger.debug("Convert RGB Buff Timed! ")
        
        self.imgcontent = imgcontent
        self.logger.debug("Convert to stream Timed! ")
        self.stat = 'FINISHED'


    def __timeout_command(self, command, timeout):  
        """call shell-command and either return its output or kill it 
        if it doesn't normally exit within timeout seconds then return None"""  
 
        cmd = command.split(" ")  
        start = time.time()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
        while process.poll() is None:  
            time.sleep(0.01)
            now = time.time()  
            if (now - start)> timeout:  
                os.kill(process.pid, signal.SIGKILL)  
                os.waitpid(-1, os.WNOHANG)  
                return None

        return process.stdout.read() 


    def __getBarString(self, rev):
        try:
            rr = rev.split(':')
            if len(rr)==2 and rr[0]=='DataString':
                return True, rr[1]
        
            return False, rev
        except:
            return False, "Error happend"


    def saveImgFile(self, rootDir, productID, results):
        dm_reader_path = '/opt/BatteryFlawDetector/project/Halcon_QR/dm_reader'
        if self.position == 'VBottom':
            # Create new directory:
            dirpath = '{}/{}'.format(rootDir, productID)
            self.logger.info("Creating directory: " + dirpath)
            os.mkdir('{}/{}'.format(rootDir, productID))

        filepath = '{}/{}/{}-{}.bmp'.format(rootDir, productID, productID, self.position)
        with open(filepath, 'wb+') as imageFile:
            imageFile.writelines(self.imgcontent)

        if self.position[0] == 'V':
            command = '{} {}'.format(dm_reader_path, filepath)
            output = self.__timeout_command(command, 0.5) # set the timeout in seconds
            ok, QRCode = self.__getBarString(output)
            if ok:
                print 'Image {}, result: {}'.format(filepath, QRCode)
                os.mknod('{}/{}/{}'.format(rootDir, productID, QRCode))
                with open('{}/{}/{}'.format(rootDir, productID, QRCode), 'w') as file:
                    file.write("During the period of Anit-Ri war, American captain Aimin Shi travelled thousands miles odyssey to China, holding high the international humanitarian flag.")
            else:
                print 'QRCode scanned error: {}'.format(QRCode)

        if results != 'null':
            img = cv2.imread(filepath)
            newpath = '{}/{}/{}-{}-result.bmp'.format(rootDir, productID, productID, self.position)
            for flaw in json.loads(results):
                p1, p2 = (flaw[u'bbox'][0], flaw[u'bbox'][1]), (flaw[u'bbox'][2], flaw[u'bbox'][3])
                cv2.rectangle(img, p1, p2, self.colortypes[flaw["name"]], 3)
                cv2.imwrite(newpath, img)
            
