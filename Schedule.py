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

if __name__ == "__main__":
    # start_time = datetime.datetime.now()
    # OSUtils.kill_APPS()
    ###Log初始化 begin###
    LogFileName = "OutBoundfixLog"+ datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d %H') +".log"
    logger.add(
        appConfig.logPath + LogFileName,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
        level="INFO",
    )
    ScheduleUtils.ControlSchedule(logger,True)