import controllers.ExcuteAlpha as ExcuteAlpha
from loguru import logger
import datetime
import config.appConfig as appConfig
import controllers.OutBoundList as OutBoundList

if __name__ == "__main__":
    LogFileName = "OutBoundfixLog"+ datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d %H') +".log"
    logger.add(
        appConfig.logPath + LogFileName,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
        level="INFO",
    )
    CheckFile = ["11.xlsx"]

    df = OutBoundList.ExcuteCheckForCancelKA8File('D:\\OutBound\\OutBoundList\\',CheckFile)
    print(df)

    ExcuteAlpha.LoginAlpha(logger)
    ExcuteAlpha.input_KA8_OutBound_For_Cancel_ByDF(logger,df)
    print("OK")