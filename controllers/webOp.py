# 导入selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
import time
import re
import os
import pyperclip
import utils.NetUtills as NetUtills
import utils.GUIUtils as GUIUtils
import config.ImgConfig as ImgConfig
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from loguru import logger
import config.appConfig as appConfig
from datetime import datetime, timedelta





def DownloadFromParts_logistics(log,deltadays):

    available_port = NetUtills.find_available_port()
    if available_port:
        log.info(f"找到一个未使用的端口: {available_port}")
    else:
        log.error("没有找到可用的端口")
        GUIUtils.Show_AlertWithMsg("请重启电脑！")
        return

    pyautogui.hotkey('winleft','r')
    pyautogui.typewrite('cmd')
    time.sleep(1)
    time.sleep(1)
    pyautogui.keyDown('enter')
    time.sleep(1)
    pyautogui.typewrite('chrome.exe --remote-debugging-port='+str(available_port)+' --user-data-dir=“D:\selenium\AutomationProfile” "http://dsz.pro.daikin.net.cn:8090/#/login";exit')
    time.sleep(1)
    pyautogui.keyDown('enter')

    options = Options()

    

    chromeaddress = "127.0.0.1:" + str(available_port)
    options.add_experimental_option("debuggerAddress", chromeaddress)

    log.info("开启浏览器")
    # 选择谷歌浏览器
    web = webdriver.Chrome(options=options)
    # return web
    windows = web.window_handles
    web.maximize_window()
    log.info("最大化浏览器")
    #web.get('http://dsz.pro.daikin.net.cn:8090/#/login')
    current_url = web.current_url
    element = None
    try:
        element = WebDriverWait(web, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/form/div[1]/div/div/input'))
        )
    except:
    #    SendMails.SendEmail('调达出库错误','部品物流系统未能登录','')###发送邮件
       log.error("部品物流系统未能登录")


    if bool(element):
        log.info("登录部品物流")
        ####输入用户名
        time.sleep(0.5)
        web.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/form/div[1]/div/div[1]/input').send_keys(appConfig.web_account)
        ####输入密码
        time.sleep(0.5)
        web.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/form/div[2]/div/div/input').send_keys(appConfig.web_password)

        if GUIUtils.waitUntilShow(logger,ImgConfig.WEB_DSZ,120):
            ####点击登录
            time.sleep(0.5)
            web.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/form/form/button/span').click()
     
    try:
        element = WebDriverWait(web, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/section/section/aside/ul/div/li/div/span'))
        )
    except:
    #    SendMails.SendEmail('调达出库错误','找不到查询页面','')###发送邮件
       log.error("找不到查询页面")

    if bool(element):
        log.info("进入查询报表")
        ####点击查询报表
        web.find_element(By.XPATH,'//*[@id="app"]/section/section/aside/ul/div/li/div/span').click()

        try:
            element = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/section/section/aside/ul/div/li/ul/div/li/span'))
            )
        except:
            # SendMails.SendEmail('调达出库错误','找不到入库明细查询','')###发送邮件
            log.error("找不到入库明细查询")
        
        ####点击出入库明细查询
        web.find_element(By.XPATH,'//*[@id="app"]/section/section/aside/ul/div/li/ul/div/li/span').click()
        
        ####点击选择出入库类型
        try:
            element = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/section/section/section/main/div/div[1]/form/div[1]/div[2]/div/div/div/div[1]/input'))
            )
        except:
            # SendMails.SendEmail('调达出库错误','找不到出入库类型','')###发送邮件
            log.error("找不到出入库类型")

        web.find_element(By.XPATH,'//*[@id="app"]/section/section/section/main/div/div[1]/form/div[1]/div[2]/div/div/div/div[1]/input').click()
        try:
            element = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/div[1]/ul/li[6]'))
            )
        except:
            # SendMails.SendEmail('调达出库错误','找不到出库（移库出）选项','')###发送邮件
            log.error("找不到出库（移库出）选项")
        ####点击出入库类型 选择 出库（移库出）
        time.sleep(0.5)
        web.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[1]/ul/li[6]').click()

        
        # #startTime
        Time_Input_Xpath_Start = "//*[@id='app']/section/section/section/main/div/div[1]/form/div[3]/div[1]/div/div/div/input[1]"
        web.find_element(By.XPATH,Time_Input_Xpath_Start).click()
        js_Start = "arguments[0].removeAttribute('readonly');"
        jsvalue_Start = "arguments[0].value = '"+ (datetime.now() + timedelta(days=deltadays)).strftime('%Y-%m-%d')+"'"

        Time_Input_Start  = web.find_element(by = By.XPATH,value = Time_Input_Xpath_Start)
        
        
        # #删除readonly
        web.execute_script(js_Start,Time_Input_Start)
        # #给input 赋值
        web.execute_script(jsvalue_Start,Time_Input_Start)
        # #startTime

        # #EndTime
        Time_Input_Xpath_Start = "//*[@id='app']/section/section/section/main/div/div[1]/form/div[3]/div[1]/div/div/div/input[2]"
        js_Start = "arguments[0].removeAttribute('readonly');"
        jsvalue_Start = "arguments[0].value = '"+ (datetime.now()).strftime('%Y-%m-%d')+"'"

        Time_Input_Start  = web.find_element(by = By.XPATH,value = Time_Input_Xpath_Start)
        
        
        # #删除readonly
        web.execute_script(js_Start,Time_Input_Start)
        # #给input 赋值
        web.execute_script(jsvalue_Start,Time_Input_Start)
        # #EndTime

        
        GUIUtils.clickByImg(logger,ImgConfig.WEB_TO,-20,0,0.9)
        
        pyautogui.hotkey('shift','home')
        pyperclip.copy((datetime.now() + timedelta(days=deltadays)).strftime('%Y-%m-%d'))
        pyautogui.hotkey('ctrl','v')
        log.info("点击查询")
        ####点击查询
        GUIUtils.clickByImg(logger,ImgConfig.WEB_SEARCH,0,0,0.9)
        # web.find_element(By.XPATH,'//*[@id="app"]/section/section/section/main/div/div[1]/form/div[4]/button[1]/span').click()
        try:
            element = WebDriverWait(web, 180).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/section/section/section/main/div/div[2]/div[2]/ul/li[1]'))
            )
        except:
            # SendMails.SendEmail('调达出库错误','查询超时','')###发送邮件
            log.error("查询超时")
        ####点击导出
        log.info("点击导出")
        
        web.find_element(By.XPATH,'//*[@id="app"]/section/section/section/main/div/div[1]/form/div[4]/button[2]/span').click()
        try:
            element = WebDriverWait(web, 1).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div[3]/button[2]'))
            )
            web.find_element(By.XPATH,'/html/body/div[3]/div/div[3]/button[2]').click()
        except:
            try:
                element = WebDriverWait(web, 1).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[3]/button[2]/span'))
                )
                web.find_element(By.XPATH,'/html/body/div[4]/div/div[3]/button[2]/span').click()
            except:
                log.error("无法点击导处确定")
        ####点击确定
        

        OutBoundList = CheckDownLoadFiles(appConfig.workPath,20)
        time.sleep(1)
        web.close()
        
        pyautogui.typewrite('exit')
        pyautogui.keyDown('enter')
        return OutBoundList

def CheckDownLoadFiles(workPath,timeout = 20):
    OutBound_files = []
    
    starttime = time.time()
    while time.time() - starttime < timeout:
        files = os.listdir(workPath)
        os.chdir(workPath)
        prefix = "出入库明细表"
        #########用正则表达式匹配文件
        pattern = re.compile(f'^{prefix}.*')
        for file in files:
            if pattern.match(file) and file.endswith('.xlsx'):
                OutBound_files.append(file)
        if len(OutBound_files)>0:
            return OutBound_files        
        else:
            time.sleep(0.1)
        
    return OutBound_files