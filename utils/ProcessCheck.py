import os
import time
import config.appConfig as appConfig
import utils.Wechat as Wechat
import datetime
from loguru import logger
 
 
def parse_output(output):
    
    pid_list = []
    lines = output.strip().split("\n")
    if len(lines) > 2:
        for line in lines[2:]:
            pid_list.append(line.split()[1])
    return pid_list
 
 
def list_not_response(process_name):
    return list_process(process_name, True)
 
 
def list_process(process_name, not_respond=False):
    cmd = 'tasklist /FI "IMAGENAME eq %s"'
    if not_respond:
        cmd = cmd + ' /FI "STATUS eq Not Responding"'
    output = os.popen(cmd % process_name)
    return parse_output(output.read())
 
 
def start_program(program):
    os.popen(program)
 
 
def check_job(process_name):
    not_respond_list = list_not_response(process_name)
    if len(not_respond_list) <= 0:
        return False
    else:
        return True
    
def Continue_CheckAlpha():
    LogFileName = "OutBoundfixProcessCheckErrorLog"+ datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d %H') +".log"
    logger.add(
        appConfig.logPath + LogFileName,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
        level="INFO",
    )
    while True:
        res1 = check_job("GSB_BSK02400.exe")
        res2 = check_job("GSB_BSK02300.exe")
        res3 = check_job("GenTabSvrDB2.exe")
        
        if res1 or res2 or res3:
            # print("Alpha连接失败！，请确认网络连接")
            logger.error("Alpha未响应，请确认Alpha状态")
            try:
                Wechat.Send("Alpha未响应，请确认Alpha状态",True,"错误",False)
            except:
                logger.error("无法连接企业微信！请确认网络连接")
        
        time.sleep(1)