import controllers.webOp as webOp
import controllers.OutBoundList as OutBoundList
import controllers.ExcuteAlpha as ExcuteAlpha
import config.appConfig as appConfig
from loguru import logger
import datetime
import utils.GUIUtils as GUIUtils
import utils.OSUtils as OSUtils
import utils.Wechat as Wechat
import utils.ScheduleUtils as ScheduleUtils
import config.ImgConfig as ImgConfig
import time


def main():
    
    start_time = datetime.datetime.now()
    OSUtils.kill_APPS()
    ###Log初始化 begin###
    LogFileName = "OutBoundfixLog"+ datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d %H') +".log"
    logger.add(
        appConfig.logPath + LogFileName,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
        level="INFO",
    )
    
    #关闭计划任务
    ScheduleUtils.ControlSchedule(logger,False)
    #Log初始化 end###
    # workFile = "出入库明细表20250227134504.xlsx"
    # df =  OutBoundList.ExcuteExcel(appConfig.workPath,workFile,logger)
    # ExcuteAlpha.LoginAlpha(logger)
    # # ExcuteAlpha.LoginAlpha(logger)
    # ExcuteAlpha.ALPHA_OUTBOUND(logger,df,workFile)
    # ExcuteAlpha.ALPHA_OVER()
    ##存档
    # OutBoundList.SaveExcels(logger)
    OutBoundList.SaveFlies(logger)
    #显示对话框
    confirm,starttime,endtime = GUIUtils.ShowMessageBox()
    
    
    
    if confirm == '取消':
        logger.info('取消KA5销账')
    elif confirm == '销账':
        GUIUtils.Show_Alert()
        #登录ALPHA
        ExcuteAlpha.LoginAlpha(logger)
        logger.info('开始销账')
        #启动ALPHA销账程序
        OutBound_Write_OffDF = ExcuteAlpha.ALPHA_OUTBOUND_Write_Off(logger,confirm)
        #关闭ALPHA
        ExcuteAlpha.ALPHA_OVER(logger)
        if not OutBound_Write_OffDF.empty:
            #保存销账数据
            OutBoundList.SaveCheckDF(OutBound_Write_OffDF,appConfig.ExcutePath,"KA5销账项"+ datetime.datetime.strftime(datetime.datetime.today(),'%Y%m%d%H%M%S') +".xlsx",logger)
            logger.info('开始销账')
            Wechat.Send_ExcuteFiles(appConfig.ExcutePath)
            Wechat.Send("销账完成！详情请见附件!",True,"正常",False)
            OutBoundList.SaveFlies(logger)
        else:
            GUIUtils.ShowWrite_OFF_ERROR()
        
    else:
        deltaDays = datetime.datetime.strptime(starttime,"%Y-%m-%d %H:%M:%S") - start_time
        
        Wechat.Send("一楼出库辅助程序开始出库",True,"正常",False)
        GUIUtils.Show_Alert()
        try:
            ##从部品物流系统下载Excel
            OutBound_files = webOp.DownloadFromParts_logistics(logger,deltaDays.days)
        except Exception as e:
            logger.error(f"发生了一个异常：{e}")
            # SendMails.SendEmail("出库信息","出库错误！请检查RPA电脑设置！",'','')
            Wechat.Send("出库错误！请检查RPA电脑设置！",True,"错误",False)
        # OutBound_files = OutBoundList.MoveDownLoadFiles(appConfig.downloadUrl,appConfig.workPath)
        logger.info("移动出入库明细表")
        if len(OutBound_files) > 0:
            for file in OutBound_files:
                try:
                    ##处理Excel
                    df,filterTimeStart,filterTimeEnd =  OutBoundList.ExcuteExcel(appConfig.workPath,file,starttime,endtime,logger)
                except:
                    Wechat.Send("RPA出库运行失败，请确认电脑设置!",True,"错误",False)
                    
                if not df.empty:
                    Wechat.Send("共需出库" + str(len(df)) +"条数据",True,"正常",False)
                    Wechat.Send("开始时间：" + filterTimeStart + "\r结束时间：" + filterTimeEnd ,True,"正常",False)
                    #登录ALPHA
                    ExcuteAlpha.LoginAlpha(logger)
                    #ALPHA处理查询
                    errordf = ExcuteAlpha.ALPHA_OUTBOUND(logger,df,file,confirm,starttime,endtime)
                    #关闭ALPHA
                    ExcuteAlpha.ALPHA_OVER(logger)
                    if not errordf.empty:
                        #保存错误项
                        OutBoundList.SaveKA5ERRORDF(errordf,appConfig.ExcutePath,"KA5销账错误项" + datetime.datetime.strftime(datetime.datetime.today(),'%Y%m%d%H%M%S') + ".xlsx",logger)
                        
                        Wechat.Send("出库有错误！请确认《出库错误项》文件!",True,"错误",False)
                    #保存销账项
                    OutBoundList.SaveCheckDF(df,appConfig.ExcutePath,"一楼KA5销账项"+ datetime.datetime.strftime(datetime.datetime.today(),'%Y%m%d%H%M%S') +".xlsx",logger)
                        
                    Wechat.Send_ExcuteFiles(appConfig.ExcutePath)
                    ExcuteAlpha.ALPHA_OUTBOUND_Write_Off(logger,'销账')
                    
                    end_time = datetime.datetime.now()
                    run_time = end_time - start_time
                    hour,min,second = OSUtils.seconds_to_hms(run_time.total_seconds())
                    Wechat.Send("出库完成！\r程序运行时间为："+str(int(hour)).zfill(2) +":"+ str(int(min)).zfill(2) + ":" + str(int(second)).zfill(2),True,"正常",False)
                    
                else:
                    Wechat.Send_ExcuteFiles(appConfig.workPath)
                    end_time = datetime.datetime.now()
                    run_time = end_time - start_time
                    hour,min,second = OSUtils.seconds_to_hms(run_time.total_seconds())
                    Wechat.Send("没有需要出库部品！\r程序运行时间为："+str(int(hour)).zfill(2) +":"+ str(int(min)).zfill(2) + ":" + str(int(second)).zfill(2),True,"错误",False)
                    
                OutBoundList.SaveFlies(logger)
                    
        else:
            logger.warning("没有出入库明细表导出到处理文件夹中")
            Wechat.Send("没有出入库明细表导出到处理文件夹中!",True,"错误",False)
            # SendMails.SendEmail("出库信息","没有出入库明细表导出到处理文件夹中",'','')
            OutBoundList.SaveFlies(logger)
    #启动计划任务
    ScheduleUtils.ControlSchedule(logger,True)




            
