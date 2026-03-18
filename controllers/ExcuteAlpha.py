import pyautogui
import utils.GUIUtils as GUIUtils
import config.ImgConfig as ImgConfig
import time
import config.appConfig as appConfig
import pyperclip
import pandas as pd
import controllers.OutBoundList as OutBoundList
from datetime import datetime,timedelta
import threading

condition = threading.Condition()

def LoginAlpha(logger):
    logger.info("登录Alpha")
    ####启动 Alpha###
    pyautogui.hotkey('winleft','r')
    pyautogui.typewrite('C:\Program Files (x86)\DAPICS\Bin\DapicsMenu.exe')
    pyautogui.keyDown('enter')
    ####启动 Alpha###
    ####输入账号####
    try:
        
        GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_LOGIN_ACCOUNT,-30,15,0.5,ImgConfig.ALPHA_LOGIN_ACCOUNT,10)
        
    except:
        logger.error("找不到Alpha输入账号位置")
        return
    
        
    pyautogui.press("backspace",presses=10)
    pyautogui.typewrite(appConfig.Alpha_Account)
    pyautogui.keyDown('enter')
    
    ####输入账号####
    ####输入密码####
    try:
        
        GUIUtils.clickByImg(logger,ImgConfig.ALPHA_LOGIN_PWD,10,7,0.5)
    except:
        logger.error("找不到Alpha输入密码位置")
        return
        
    pyautogui.typewrite(appConfig.Alpha_PassWord)
    pyautogui.keyDown('enter')
    logger.info("登录成功")
    ####输入密码####

def ALPHA_OUTBOUND(logger,df,workFile,status,starttime,endtime):
    
    

    logger.info("KA5 要求信号部品出货指示开始")
    errordf = input_KA5_Instruction_ByDF(logger,df)
    
    logger.info("KA5 要求信号部品出货指示结束")

    
    # logger.info("KA7 出库指示进度查询开始")
    # CheckFile = search_KA7_ByDF(logger,workFile.replace('出入库明细表','').replace('.xlsx','') + "CheckFile.xlsx",status,starttime,endtime)
    # if len(CheckFile) == 0:
    #     return
    # logger.info("KA7 出库指示进度查询结束")
    # # CheckFile = '2025021220250212141140CheckFile.xlsx'
    
    # OutBoundDF = OutBoundList.ExcuteCheckFile(appConfig.CheckFilePath,CheckFile)
    
        
    # print(OutBoundDF)
    # logger.info("KA8 通常出库登记开始")
    # input_KA8_OutBound_ByDF(logger,OutBoundDF)
    # logger.info("KA8 通常出库登记结束")
    return errordf

def ALPHA_OUTBOUND_Write_Off(logger,status):
    
    


    logger.info("KA7 出库指示进度查询开始")
    CheckFile = search_KA7_ByDF(logger,datetime.now().strftime("%H%M%S") + '.xlsx',status)
    if len(CheckFile) == 0:
        return
    logger.info("KA7 出库指示进度查询结束")
    # CheckFile = ["20250407100830.xlsx"]
    OutBoundDF = OutBoundList.ExcuteCheckFile(appConfig.CheckFilePath,CheckFile)
    
        
    print(OutBoundDF)
    logger.info("KA8 通常出库登记开始")
    input_KA8_OutBound_ByDF(logger,OutBoundDF)
    logger.info("KA8 通常出库登记结束")
    return OutBoundDF
    


def input_KA5_Instruction_ByDF(logger,df):
    
    errrordf = pd.DataFrame(columns=['图号', '工程', '累进', '货架', '数量', '仓库', '日期'])
    ###点击 KA5###
    try:
        
        GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_KA5,10,7,0.5,ImgConfig.ALPHA_KA5,2)
        
    except:
        logger.error("找不到KA5")
        return errrordf
    ###点击最大化窗口###
    GUIUtils.maxWindowUntilShow(logger,ImgConfig.ALPHA_KA5_TITLE,3)
    
    ### 输入仓库号码 1 ####
    pyautogui.typewrite('1')

    ### 输入供应场所 311###
    pyautogui.press("Tab")
    pyautogui.typewrite('311')

    ### 输入备考 ###
    pyautogui.press("Tab",presses=3)
    pyperclip.copy("依部品物流系统出库明细出库")
    try:
        GUIUtils.rightClickByImg(logger,ImgConfig.ALPHA_OUTBOUND_REMARK,10,7,0.5)
        pyautogui.keyDown("P")
    except:
        logger.error("找不到备考")
        return errrordf 
    
    for index,row in df.iterrows():

        GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA5_CLEAR,0,0,0.9)
        GUIUtils.DoubleclickByImg(logger,ImgConfig.ALPHA_OUTBOUND_IMGNO,10,20,0.7)
        ### 输入图号 ###
        
        pyautogui.typewrite(row['图号'])

        ### 输入工程 ###
        
        if pd.isna(row['工程']):
            
            pass
        else:
            
            GUIUtils.DoubleclickByImg(logger,ImgConfig.ALPHA_KA5_PROJ,10,20,0.7)
            pyautogui.typewrite(str(row['工程']))

        ### 输入累进 ###
        
        if pd.isna(row['累进']):
            GUIUtils.DoubleclickByImg(logger,ImgConfig.ALPHA_KA5_STOCK,10,5,0.7)
            
        else:
            GUIUtils.DoubleclickByImg(logger,ImgConfig.ALPHA_KA5_VERSION,10,5,0.7)
            pyautogui.typewrite(row['累进'])
            
        GUIUtils.DoubleclickByImg(logger,ImgConfig.ALPHA_KA5_STOCK,10,5,0.7)
        
        ### 输入货架 ###
        
        pyautogui.typewrite(row['货架'])

        ### 点击查询 ###
        GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA5_SEARCH,10,5,0.7)
        # time.sleep(5)
        ### 输入变区 ###
        # pyautogui.press("Tab")
        logger.info(f"填写出库指示信息----图号:{row['图号']} , 工程:{row['工程']} , 累进:{row['累进']} , 货架:{row['货架']} , 数量:{row['数量']}, 日期:{row['日期']}")
        
        
        if GUIUtils.waitUntilShow(logger,ImgConfig.ALPHA_KA5_ERROR_LOGO,0.3):
            logger.error(f"填写出库指示信息出错----仓库No:{str(row['仓库'])} , 图纸号码:{row['图号']} , 工程:{row['工程']} , 累进:{row['累进']} , 货架:{row['货架']} , 数量:{str(row['数量'])}, 日期:{row['日期']}")
            errrordf = errrordf._append(row, ignore_index=True)
            # GUIUtils.screenShootERROR(ImgConfig.ALPHA_KA5_ERROR_LOGO)
            # pyautogui.keyDown('enter')
            ##线程同步##
            threadPhoto = threading.Thread(target=SaveErrorPhoto)
            threadEnter = threading.Thread(target=Enter)
            threadPhoto.start()
            threadEnter.start()
            threadPhoto.join()
            threadEnter.join()
            continue
        if GUIUtils.enterUntilShow(logger,ImgConfig.ALPHA_KA5_SEARCH_ERROR,0.3):
            logger.info('点击注意按钮')

        pyautogui.keyDown('2')
        
        ### 输入数量 ###
        pyautogui.keyDown('enter')
        pyautogui.press("Tab")
        pyautogui.typewrite(str(row['数量']))
        pyautogui.press("ctrl")
        
        
        if GUIUtils.waitUntilShow(logger,ImgConfig.ALPHA_KA5_ERROR_LOGO,0.6):
            logger.error(f"填写出库指示信息出错----仓库No:{str(row['仓库'])} , 图纸号码:{row['图号']} , 工程:{row['工程']} , 累进:{row['累进']} , 货架:{row['货架']} , 数量:{str(row['数量'])}, 日期:{row['日期']}")
            errrordf = errrordf._append(row, ignore_index=True)
            # GUIUtils.screenShootERROR(ImgConfig.ALPHA_KA5_ERROR_LOGO)
            # pyautogui.keyDown('enter')
            ##线程同步##
            threadPhoto = threading.Thread(target=SaveErrorPhoto)
            threadEnter = threading.Thread(target=Enter)
            threadPhoto.start()
            threadEnter.start()
            threadPhoto.join()
            threadEnter.join()
            # GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA5_CONFIRM,0,0,0.9)
            continue
        # 处理排他错误
        if GUIUtils.enterUntilShow(logger,ImgConfig.ALPHA_KA5_SEARCH_ERROR,0.3):
            pyautogui.press("ctrl")
            logger.info('点击注意按钮')

        if GUIUtils.waitUntilShow(logger,ImgConfig.ALPHA_KA5_SAVE,10):
            filename = datetime.strptime(str(row['日期']), "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S") + row['图号'] + str(index).zfill(4) + str(row['数量'])
            pyautogui.typewrite(OutBoundList.sanitize_windows_filename(filename))
            try:
                # GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA5_SAVE,10,7,0.9)
                pyautogui.keyDown('enter')
                if GUIUtils.waitUntilShow(logger,ImgConfig.ALPHA_KA5_PRINT,1.2,False):
                    logger.info(f"wait for print")
                    if GUIUtils.wait_for_image_to_disappear(ImgConfig.ALPHA_KA5_PRINT,0.9,0.1):
                        logger.info(f"填写出库指示信息----图号:{row['图号']} , 工程:{row['工程']} , 累进:{row['累进']} , 货架:{row['货架']} , 数量:{row['数量']}, 日期:{row['日期']}")
            except Exception as e:
                logger.info("保存PDF"+f"-仓库No:{str(row['仓库'])} , 图纸号码:{row['图号']} , 工程:{row['工程']} , 累进:{row['累进']} , 货架:{row['货架']} , 数量:{str(row['数量'])}, 日期:{row['日期']}"+ f"Exception:{e}")    
        else:
            logger.error("保存PDF失败"+f"-仓库No:{str(row['仓库'])} , 图纸号码:{row['图号']} , 工程:{row['工程']} , 累进:{row['累进']} , 货架:{row['货架']} , 数量:{str(row['数量'])}, 日期:{row['日期']}")
        print("OK")


    time.sleep(1)
    GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_OVER,0,0,0.9,ImgConfig.ALPHA_OVER,10)
    return errrordf
    
    

def input_KA8_OutBound_ByDF(logger,df):

    ###点击 KA8###
    try:
        
        GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_KA8,0,0,0.9,ImgConfig.ALPHA_KA8,3)
        logger.info("点击KA8")
        # GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA5,10,7,0.5)
    except:
        logger.error("找不到KA8")
        return

    ###点击最大化窗口###
    GUIUtils.maxWindowUntilShow(logger,ImgConfig.ALPHA_KA8_TITLE,3)
    
    
    ### 输入仓库号码 1 ####
    pyautogui.typewrite('RPA')
    pyautogui.press('shift')
    ### 输入供应场所 311###
    pyautogui.press("Tab")
    
    for index,row in df.iterrows():
        print(row)
        ### 输入出库指示No ###
        ##线程同步##
        threadTypeWrite = threading.Thread(target=TypeWrite,args=[str(row["出库指示No"])])
        threadClick = threading.Thread(target=ClickSearch,args=[logger])
        threadConfirm = threading.Thread(target=ClickConfirm,args=[logger])
        # threadEnter = threading.Thread(target=Enter)
        # threadTab = threading.Thread(target=Tab)
        # threadCtrl = threading.Thread(target=Ctrl)
        threadTypeWrite.start()
        threadTypeWrite.join()
        threadClick.start()
        threadClick.join()
        threadConfirm.start()
        threadConfirm.join()
        if GUIUtils.enterUntilShow(logger,ImgConfig.ALPHA_KA5_ERROR,0.3):
            logger.info('点击排他按钮')
        # threadCtrl.start()
        # threadCtrl.join()
        # pyautogui.typewrite(str(row["出库指示No"]))
        # pyautogui.press("Tab")
        # pyautogui.press("enter")
        # # pyautogui.typewrite('3')
        # pyautogui.press("ctrl")
        # # pyautogui.press("enter",presses=2)
        # # pyautogui.press("Tab")
        logger.info(f"填写出库信息----出库指示No:{row["出库指示No"]}")

    time.sleep(1)
    GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_OVER,0,0,0.9,ImgConfig.ALPHA_OVER,10)

def input_KA8_OutBound_For_Cancel_ByDF(logger,df):

    ###点击 KA8###
    try:
        
        GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_KA8,0,0,0.9,ImgConfig.ALPHA_KA8,3)
        logger.info("点击KA8")
        # GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA5,10,7,0.5)
    except:
        logger.error("找不到KA8")
        return

    ###点击最大化窗口###
    GUIUtils.maxWindowUntilShow(logger,ImgConfig.ALPHA_KA8_TITLE,3)
    
    
    ### 输入仓库号码 1 ####
    pyautogui.typewrite('RPA')
    pyautogui.press('shift')
    ### 输入供应场所 311###
    pyautogui.press("Tab")
    
    for index,row in df.iterrows():
        print(row)
        ### 输入出库指示No ###
        ##线程同步##
        threadTypeWrite = threading.Thread(target=TypeWrite,args=[str(row["出库指示No"])])
        threadClick = threading.Thread(target=ClickSearch,args=[logger])
        threadConfirm = threading.Thread(target=ClickConfirm,args=[logger])
        threadPress3 = threading.Thread(target=Press3)
        threadEnter = threading.Thread(target=Enter)
        # threadTab = threading.Thread(target=Tab)
        # threadCtrl = threading.Thread(target=Ctrl)
        threadTypeWrite.start()
        threadTypeWrite.join()
        # if GUIUtils.enterUntilShow(logger,ImgConfig.ALPHA_KA5_ERROR,0.3):
        #     logger.info('点击注意按钮')
        #     pyautogui.press("enter")
        #     continue
        # time.sleep(3)
        threadClick.start()
        threadClick.join()
        # time.sleep(3)
        threadPress3.start()
        threadPress3.join()
        # time.sleep(3)
        threadConfirm.start()
        threadConfirm.join()
        # time.sleep(3)
        threadEnter.start()
        threadEnter.join()
        time.sleep(3)
        threadEnter.join()
        if GUIUtils.enterUntilShow(logger,ImgConfig.ALPHA_KA5_ERROR,0.3):
            logger.info('点击排他按钮')
            pyautogui.press("enter")
            # time.sleep(3)
        # threadCtrl.start()
        # threadCtrl.join()
        # pyautogui.typewrite(str(row["出库指示No"]))
        # pyautogui.press("Tab")
        # pyautogui.press("enter")
        # # pyautogui.typewrite('3')
        # pyautogui.press("ctrl")
        # # pyautogui.press("enter",presses=2)
        # # pyautogui.press("Tab")
        logger.info(f"填写出库信息----出库指示No:{row["出库指示No"]}")

    time.sleep(1)
    GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_OVER,0,0,0.9,ImgConfig.ALPHA_OVER,10)
    
def search_KA7_ByDF(logger,workFile,status):

    CheckFiles = []
    CheckFileName = workFile
    
    days = []
    now = datetime.now()
    if status == "销账":
        days.append((now - timedelta(days=1)).strftime("%Y%m%d"))
        # days.append((now).strftime("%Y%m%d"))
        # days.append((datetime.now() + timedelta(days=-10)).strftime("%Y%m%d"))
        # days.append((datetime.now() + timedelta(days=-10)).strftime("%Y%m%d"))
        # days.append((datetime.now() + timedelta(days=-9)).strftime('%Y%m%d'))
        
    else:
        days.append((now - timedelta(days=1)).strftime("%Y%m%d"))
        days.append((now).strftime("%Y%m%d"))
        # starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d")
        # endtime = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d")
        # if starttime == endtime:
        #     days.append(starttime)
        # else:
        #     days.append(starttime)
        #     days.append(endtime)

    ##点击 KA7###
    try:
        
        GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_KA7,10,7,0.5,ImgConfig.ALPHA_KA7,2)
        logger.info("点击KA7")
        # GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA5,10,7,0.5)
    except:
        logger.error("找不到KA7")
        return CheckFiles
    ###点击最大化窗口###
    GUIUtils.maxWindowUntilShow(logger,ImgConfig.ALPHA_KA7_TITLE,3)

    for day in days:
        
        
        ###点击发行指示日###
        try:
            GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA7_INSTRUCTION_DATE,10,7,0.5)
            logger.info(f"点击发行指示日")
        except:
            logger.error("找不到发行指示日")
            return CheckFiles
        pyautogui.typewrite(day)

        ###点击查询###
        try:
            GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA7_SEARCH,10,7,0.5)
            logger.info(f"点击查询")
        except:
            logger.error("找不到查询按钮")
            return CheckFiles
        ###判断有没有数据
        if GUIUtils.enterUntilShow(logger,ImgConfig.ALPHA_KA7_ERROR,0.5):
            logger.error(f"KA7 {day} 没有数据")
            pyautogui.keyDown('enter')
            continue
        
        ###点击TITLE###
        try:
            GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA7_TITLE,10,7,0.5)
            logger.info(f"点击TITLE")
        except:
            logger.error("找不到TITLE")
            return CheckFiles
        
        ###点击保存Excel按钮###
        try:
            GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_KA7_SAVE,0,0,0.9,ImgConfig.ALPHA_KA7_CHECK_SEARCH_RESULT,120)
            logger.info(f"点击保存Excel按钮")
        except:
            logger.error("找不到保存Excel按钮")
            return CheckFiles
        ###点击弹窗保存按钮###
        try:
            if GUIUtils.typeWritewithShiftUntilShow(logger,day+CheckFileName,ImgConfig.ALPHA_KA7_SAVEFILE,10):
                pyautogui.press('enter')
                logger.info(f"点击弹窗保存按钮")
            else:
                logger.error("找不到弹窗保存按钮")
                return CheckFiles
        except:
            logger.error("找不到弹窗保存按钮")
            return CheckFiles

        ###点击输出完成提示###
        try:
            GUIUtils.enterUntilShow(logger,ImgConfig.ALPHA_KA7_OUTPUT_FINISH,60)
            logger.info(f"点击输出完成提示")
        except Exception as e:
            print(e)
            logger.error("找不到输出完成提示")
            return CheckFiles
        CheckFiles.append(day+CheckFileName)
    ###点击退出###
    try:
        GUIUtils.clickByImg(logger,ImgConfig.ALPHA_KA7_EXIT,0,0,0.9)
        logger.info(f"点击查询")
    except:
        logger.error("找不到查询按钮")
        return CheckFiles
    return CheckFiles

def ALPHA_OVER(logger):
    time.sleep(1)
    GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_OVER,0,0,0.9,ImgConfig.ALPHA_OVER,10)
    # GUIUtils.clickByImg(logger,ImgConfig.ALPHA_OVER,0,0,0.9)

def SaveErrorPhoto():
    with condition:
        GUIUtils.screenShootERROR(ImgConfig.ALPHA_KA5_ERROR_LOGO)

def Enter():
    with condition:
        pyautogui.press('enter')

def Tab():
    with condition:
        pyautogui.keyDown('Tab')
def Ctrl():
    with condition:
        pyautogui.keyDown('ctrl')

def Press3():
    with condition:
        pyautogui.press('3')

def ClickSearch(logger):
    with condition:
        GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_KA5_SEARCH,0,0,0.9,ImgConfig.ALPHA_KA5_SEARCH,120)
def ClickConfirm(logger):
    with condition:
        GUIUtils.clickUntilShow(logger,ImgConfig.ALPHA_KA8_CONFIRM_CTRL,0,0,0.9,ImgConfig.ALPHA_KA8_CONFIRM_CTRL,120)    

def TypeWrite(str_OutBoundInst):
    with condition:
        pyautogui.typewrite(str_OutBoundInst)    
    