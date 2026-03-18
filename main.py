import config.appConfig as appConfig
from loguru import logger

import OutBoundFixAssemble as outbound
from multiprocessing import Process
import utils.NetUtills as NetUtills
import utils.ProcessCheck as ProcessCheck
# import utils.GUIUtils as GUIUtils
# import config.ImgConfig as ImgConfig
# import time
from multiprocessing import Process,Queue
import utils.SreenRecord as SreenRecord
import time

if __name__ == "__main__":
    ###Log初始化 begin###
    Stop_queue = Queue()
    processnet = Process(target = NetUtills.continue_Ping)
    processnet.daemon = True 
    processnet.start()
    processexe = Process(target = ProcessCheck.Continue_CheckAlpha)
    processexe.daemon = True 
    processexe.start()
    processrecord = Process(target = SreenRecord.Record,args=(Stop_queue,))
    processrecord.daemon = True 
    processrecord.start()
    try:
        outbound.main()
        time.sleep(3)
    except:
        Stop_queue.put("Stop")
    finally:
        Stop_queue.put("Stop")
    
    

    
    
    