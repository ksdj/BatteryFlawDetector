/**
* @file   ImageConvert.h
* @brief  ͼ���ʽת��.
* @author qi_zhiyu
* @par    Copyright (c):
*         ZheJiang Dahua Technology Stock Co.Ltd.
*         All Rights Reserved
* @version 1.0.0.1
*/

#ifndef __IMAGE_CONVERT_H_
#define __IMAGE_CONVERT_H_

#ifdef  __cplusplus
extern "C"{
#endif  // end #ifdef  __cplusplus

#ifdef WIN64
#undef WIN32
#endif

	/** ����ѡ�� */
#ifdef WIN32  // win64λ�£��ᱨ��def�ظ�����ľ��� In Win 64bit, it will report warning for duplicate definition
#  ifdef _USRDLL // ��̬�⵼�� Export DLL
#    ifdef IMAGECONVERT_EXPORTS
#		define IMGCNV_API __declspec(dllexport)
#	 else
#		define IMGCNV_API __declspec(dllimport)
#	 endif
#  else
#    define IMGCNV_API
#  endif // end of ifdef _USRDLL
#else
#	define IMGCNV_API
#endif //end #ifdef WIN32

#if (defined (WIN32) || defined(WIN64))
#   define CALLMETHOD __stdcall
#else
#	define CALLMETHOD
#endif // end #if (defined (WIN32) || defined(WIN64))

	typedef void* IMGCNV_HANDLE;        ///< ת��APIʹ�õľ�� Handle for using conversion API

	/**
	* @enum IMGCNV_EErr
	* @brief �ӿڷ���ֵ Return value
	* @attention �� No
	*/
	typedef enum tagIMGCNV_EErr
	{
		IMGCNV_SUCCESS,
		IMGCNV_ILLEGAL_PARAM,			 ///< �Ƿ����� Illegal parameter
		IMGCNV_ERR_ORDER,                ///< ���ýӿ�˳����� Sequence error for calling interfaces
		IMGCNV_NO_MEMORY,				 ///< �ڴ治�� No memory
		IMGCNV_NOT_SUPPORT,              ///< ��֧��   Not support
	}IMGCNV_EErr;

	typedef struct tagIMGCNV_SOpenParam
	{
		int width;							///< ͼ��� Image width
		int height;							///< ͼ��� Image Height
		int paddingX;						///< ͼ������ Padding X
		int paddingY;						///< ͼ������ Padding Y
		int dataSize;						///< ͼ���С   Image size
		unsigned int pixelForamt;			///< Դͼ���ͼ���ʽ Image format of source image
	}IMGCNV_SOpenParam;

	/**
    *  ~chinese  
	*  @brief  ת��ΪBGR24��ת������
	*  @param[in] pSrcData		��Դ����
	*  @param[in] pOpenParam	��IMGCNV_SOpenParam�ṹ��,��ʽת������Ҫ�Ĳ���
	*  @param[out]pDstData		��ת���������	
	*  @param[out]pDstDataSize	��ת�������ݵĳ���	
	*  @Return:   IMGCNV_ERR_E  : ͼ���ʽת���ӿڷ���ֵ
	*  - IMGCNV_SUCCESS ��ʾִ�гɹ�
	*  - ����ֵ��IMGCNV_ERR_Eö��
	*  �ر�˵��
	*  ���ظ�ʽΪYUV411Packed��ʱ��ͼ������ܱ�4����
	*  ���ظ�ʽΪYUV422Packed��ʱ��ͼ������ܱ�2����
	*  ���ظ�ʽΪYUYVPacked��ʱ��ͼ������ܱ�2����
	*  ת�����ͼ��:���ݴ洢�Ǵ��������һ�п�ʼ�ģ������������ݵ�Ĭ�ϴ洢����
	*  ~english  
	*  @brief  convert to BGR24
	*  @param[in] pSrcData		��source data
	*  @param[in] pOpenParam	��conversion required paraneters
	*  @param[out]pDstData		��converted data
	*  @param[out]pDstDataSize	��length of converted data 
	*  @Return:   IMGCNV_ERR_E	:return value
	*  - IMGCNV_SUCCESS return ok
	*  - Other values refers to enumeration of IMGCNV_ERR_E 
	*  Special note
	*  pixelFormat:YUV411Packed,the image width is divisible by 4
	*  pixelFormat:YUV422Packed,the image width is divisible by 2
	*  pixelFormat:YUYVPacked��the image width is divisible by 2
	*  converted image��The first row of the image is located at the start of the image buffer.This is the default for image taken by a camera.
	*/
	IMGCNV_API IMGCNV_EErr CALLMETHOD IMGCNV_ConvertToBGR24(unsigned char* pSrcData, IMGCNV_SOpenParam* pOpenParam, unsigned char* pDstData, int* pDstDataSize);

	/**
    *  ~chinese  
	*  @brief  ת��ΪRGB24��ת������
	*  @param[in] pSrcData		��Դ����
	*  @param[in] pOpenParam	��IMGCNV_SOpenParam�ṹ��,��ʽת������Ҫ�Ĳ���
	*  @param[out]pDstData		��ת���������	
	*  @param[out]pDstDataSize	��ת�������ݵĳ���	
	*  @Return:   IMGCNV_ERR_E  : ͼ���ʽת���ӿڷ���ֵ
	*  - IMGCNV_SUCCESS ��ʾִ�гɹ�
	*  - ����ֵ��IMGCNV_ERR_Eö��
	*  �ر�˵��
	*  ���ظ�ʽΪYUV411Packed��ʱ��ͼ������ܱ�4����
	*  ���ظ�ʽΪYUV422Packed��ʱ��ͼ������ܱ�2����
	*  ���ظ�ʽΪYUYVPacked��ʱ��ͼ������ܱ�2����
	*  ת�����ͼ��:���ݴ洢�Ǵ��������һ�п�ʼ�ģ������������ݵ�Ĭ�ϴ洢����
	*  ~english  
	*  @brief  convert to RGB24
	*  @param[in] pSrcData		��source data
	*  @param[in] pOpenParam	��conversion required paraneters
	*  @param[out]pDstData		��converted data
	*  @param[out]pDstDataSize	��length of converted data 
	*  @Return:   IMGCNV_ERR_E	:return value
	*  - IMGCNV_SUCCESS return ok
	*  - Other values refers to enumeration of IMGCNV_ERR_E 
	*  Special note
	*  pixelFormat:YUV411Packed,the image width is divisible by 4
	*  pixelFormat:YUV422Packed,the image width is divisible by 2
	*  pixelFormat:YUYVPacked��the image width is divisible by 2
	*  converted image��The first row of the image is located at the start of the image buffer.This is the default for image taken by a camera.
	*/
	IMGCNV_API IMGCNV_EErr CALLMETHOD IMGCNV_ConvertToRGB24(unsigned char* pSrcData, IMGCNV_SOpenParam* pOpenParam, unsigned char* pDstData, int* pDstDataSize);

	/**
	*  ~chinese
	*  @brief  ת��ΪMono8��ת������
	*  @param[in] pSrcData		��Դ����
	*  @param[in] pOpenParam	��IMGCNV_SOpenParam�ṹ��,��ʽת������Ҫ�Ĳ���
	*  @param[out]pDstData		��ת���������
	*  @param[out]pDstDataSize	��ת�������ݵĳ���
	*  @Return:   IMGCNV_ERR_E  : ͼ���ʽת���ӿڷ���ֵ
	*  - IMGCNV_SUCCESS ��ʾִ�гɹ�
	*  - ����ֵ��IMGCNV_ERR_Eö��
	*  �ر�˵��
	*  ���ظ�ʽΪYUV411Packed��ʱ��ͼ������ܱ�4����
	*  ���ظ�ʽΪYUV422Packed��ʱ��ͼ������ܱ�2����
	*  ���ظ�ʽΪYUYVPacked��ʱ��ͼ������ܱ�2����
	*  ת�����ͼ��:���ݴ洢�Ǵ��������һ�п�ʼ�ģ������������ݵ�Ĭ�ϴ洢����
	*  ~english
	*  @brief  convert to Mono8
	*  @param[in] pSrcData		��source data
	*  @param[in] pOpenParam	��conversion required paraneters
	*  @param[out]pDstData		��converted data
	*  @param[out]pDstDataSize	��length of converted data
	*  @Return:   IMGCNV_ERR_E	:return value
	*  - IMGCNV_SUCCESS return ok
	*  - Other values refers to enumeration of IMGCNV_ERR_E
	*  Special note
	*  pixelFormat:YUV411Packed,the image width is divisible by 4
	*  pixelFormat:YUV422Packed,the image width is divisible by 2
	*  pixelFormat:YUYVPacked��the image width is divisible by 2
	*  converted image��The first row of the image is located at the start of the image buffer.This is the default for image taken by a camera.
	*/
	IMGCNV_API IMGCNV_EErr CALLMETHOD IMGCNV_ConvertToMono8(unsigned char* pSrcData, IMGCNV_SOpenParam* pOpenParam, unsigned char* pDstData, int* pDstDataSize);

#ifdef  __cplusplus
}
#endif // end #ifdef  __cplusplus

#endif // end of #ifndef __IMAGE_CONVERT_H_