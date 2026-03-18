import socket
import time
import config.appConfig as appConfig
import datetime
from loguru import logger
import utils.Wechat as Wechat
import ping3




def is_port_in_use(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def find_available_port(start=1024, end=65535):
    for port in range(start, end + 1):
        if not is_port_in_use(port):
            return port
    return None  # 如果没有找到可用的端口
 
def ping(host, timeout=1):
    try:
        response_time = ping3.ping(host, timeout=timeout)
        if response_time is None:
            return False
        else:
            return True
    except:
        return False
 

def continue_Ping():
    LogFileName = "OutBoundfixNetErrorLog"+ datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d %H') +".log"
    logger.add(
        appConfig.logPath + LogFileName,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
        level="INFO",
    )
    while True:
        res = ping(appConfig.Alpha_IP)
        
        if not res:
            # print("Alpha连接失败！，请确认网络连接")
            logger.error("Alpha连接失败！请确认网络连接")
            try:
                Wechat.Send("ALPHA 数据库连接失败！请检查该时间段出库数量！",True,"错误",False)
            except:
                logger.error("无法连接企业微信！请确认网络连接")
        
        time.sleep(1)


# # 测试ping功能
# if __name__ == "__main__":
#     host = "www.baidu.com"
#     if ping(host):
#         print(f"{host} is reachable.")
#     else:
#         print(f"{host} is not reachable.")