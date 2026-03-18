import os
import shutil
from datetime import datetime, timedelta
from dateutil import parser
import re
import pandas as pd
import config.appConfig as appConfig
import os






################从下载路径中找出【出入库明细表】放到处理文件夹中###############
def MoveDownLoadFiles(downloadUrl,workPath):
    OutBound_files = []
    files = os.listdir(downloadUrl)
    os.chdir(downloadUrl)
    prefix = "出入库明细表"
    #########用正则表达式匹配文件
    pattern = re.compile(f'^{prefix}.*')

    for file in files:
        if pattern.match(file):
            OutBound_files.append(file)
            shutil.move(file,workPath)
    return OutBound_files


def MoveFiles(OrginUrl,workPath):
    files = os.listdir(OrginUrl)
    os.chdir(OrginUrl)
    #创建月度文件夹
    directory_path = workPath + '\\' + datetime.now().strftime("%Y%m")
    if not os.path.exists(directory_path) and not os.path.isdir(directory_path):
        os.makedirs(directory_path, exist_ok=True)
    #创建日文件夹
    directory_date_path = directory_path + '\\' + datetime.now().strftime("%d")
    if not os.path.exists(directory_date_path) and not os.path.isdir(directory_date_path):
        os.makedirs(directory_date_path, exist_ok=True)
    for file in files:
        shutil.move(file,directory_date_path)
    
def MovePDFFiles(OrginUrl,PDFSavePath):
    #创建月度文件夹
    directory_path = PDFSavePath + '\\' + datetime.now().strftime("%Y%m")
    if not os.path.exists(directory_path) and not os.path.isdir(directory_path):
        os.makedirs(directory_path, exist_ok=True)
    #创建日文件夹
    directory_date_path = directory_path + '\\' + datetime.now().strftime("%d")
    if not os.path.exists(directory_date_path) and not os.path.isdir(directory_date_path):
        os.makedirs(directory_date_path, exist_ok=True)

    #获取PDF集合
    files = [f for f in os.listdir(OrginUrl) if os.path.isfile(os.path.join(OrginUrl, f))]
    if files:
        folder_name = datetime.now().strftime("%Y%m%d%H%M")
        path = directory_date_path + "\\" + folder_name
        os.makedirs(path, exist_ok=True)
        files = os.listdir(OrginUrl)
        os.chdir(OrginUrl)
        for file in files:
            shutil.move(file,path)

def ExcuteExcel(workpath,AfterProcessedFile,start,end,logger):
    filterTimeStart,filterTimeEnd = start,end
    logger.info("处理文件:"+ AfterProcessedFile +"开始时间:"+filterTimeStart +";结束时间："+filterTimeEnd)
    df = pd.read_excel(workpath + AfterProcessedFile, dtype={'工程':str,'数量':int})
    
    stockdf = pd.read_excel(appConfig.StockExcel)
    print(df)
    mask = (df['日期'] > filterTimeStart) & (df['日期'] <= filterTimeEnd)
    filtered_df = df.loc[mask]
    print(filtered_df)
    selected_columns = ['图号', '工程', '累进', '货架','数量','仓库','日期']
    print(filtered_df[selected_columns])
    
    result = pd.merge(filtered_df[selected_columns],stockdf,on = '仓库',how='inner')
    print(result)
    
    return result,filterTimeStart,filterTimeEnd

def getExcuteDateTimeRange():
    i = datetime.now()
    print(i.strftime("%Y-%m-%d %H:%M:%S"))
    FixedTime = ""
    if i.minute > 0 and i.minute < 30:
        FixedTime = i.strftime("%Y-%m-%d %H:") + "00:00"
    else:
        FixedTime = i.strftime("%Y-%m-%d %H:") + "30:00"

    Fixedi = parser.parse(FixedTime)
    return (Fixedi+timedelta(minutes=-30)).strftime("%Y-%m-%d %H:%M:%S"),Fixedi.strftime("%Y-%m-%d %H:%M:%S")

def getExcuteDateTimeRange123(min):
    i = datetime.now()
    print(i.strftime("%Y-%m-%d %H:%M:%S"))
    FixedTime = ""
    if i.minute > 0 and i.minute < 30:
        FixedTime = i.strftime("%Y-%m-%d %H:") + "00:00"
    else:
        FixedTime = i.strftime("%Y-%m-%d %H:") + "30:00"

    Fixedi = parser.parse(FixedTime)
    return (Fixedi+timedelta(minutes=min)).strftime("%Y-%m-%d %H:%M:%S"),Fixedi.strftime("%Y-%m-%d %H:%M:%S")

def ExcuteCheckFile(workpath,CheckFile):
    totalDF = pd.DataFrame()

    if len(CheckFile) > 1:
        for file in CheckFile:
            checkdf = pd.read_excel(workpath + file,header=6)
            # print(checkdf)
            mask = (checkdf['完了符'] != '1') & (checkdf['发行者'] == 'RPA-OT')
            filtered_df = checkdf.loc[mask]
            if not filtered_df.empty:
                selected_columns = ['货架号', '出库指示No', '图纸号码']
                filtered_df[selected_columns]
                totalDF = pd.concat([totalDF, filtered_df[selected_columns]])
    else:
        checkdf = pd.read_excel(workpath + CheckFile[0],header=6)
        # print(checkdf)
        mask = (checkdf['完了符'] != '1') & (checkdf['发行者'] == 'RPA-OT')
        filtered_df = checkdf.loc[mask]
        if not filtered_df.empty:
                selected_columns = ['货架号', '出库指示No', '图纸号码']
                filtered_df[selected_columns]
                totalDF = pd.concat([totalDF, filtered_df[selected_columns]])
    
    return totalDF

def ExcuteCheckForCancelKA8File(workpath,CheckFile):
    totalDF = pd.DataFrame()

    if len(CheckFile) > 1:
        for file in CheckFile:
            checkdf = pd.read_excel(workpath + file,header=6)
            # print(checkdf)
            mask = (checkdf['完了符'] != '1') & (checkdf['发行者'] == 'RPA-OT')
            filtered_df = checkdf.loc[mask]
            print(filtered_df)
            if not filtered_df.empty:
                selected_columns = ['货架号', '出库指示No', '图纸号码','发行时间']
                filtered_df[selected_columns]
                totalDF = pd.concat([totalDF, filtered_df[selected_columns]])
    else:
        checkdf = pd.read_excel(workpath + CheckFile[0],header=6)
        # print(checkdf)
        mask = (checkdf['完了符'] != '1') & (checkdf['发行者'] == 'RPA-OT') 
        filtered_df = checkdf.loc[mask]
        if not filtered_df.empty:
                selected_columns = ['货架号', '出库指示No', '图纸号码','发行时间']
                filtered_df[selected_columns]
                totalDF = pd.concat([totalDF, filtered_df[selected_columns]])
    
    return totalDF


def SaveKA5ERRORDF(OutBoundDF,savepath,ErrorFile,logger):
    try:
        if not OutBoundDF.empty:
            OutBoundDF.to_excel(savepath + ErrorFile,index=False)
            logger.info("销账数据导出成功")    
    except:
        logger.error("没有数据需要销账")

def SaveCheckDF(OutBoundDF,savepath,CheckFile,logger):
    try:
        if not OutBoundDF.empty:
            OutBoundDF.to_excel(savepath + CheckFile,index=False)
            logger.info("销账数据导出成功")    
    except:
        logger.error("没有数据需要销账")

def SaveFlies(logger):
    logger.info("开始存档")
    MoveFiles(appConfig.workPath,appConfig.HistroyWorkPath)
    MoveFiles(appConfig.CheckFilePath,appConfig.HistroyCheckPath)
    MoveFiles(appConfig.ExcutePath,appConfig.HistroyExcutePath)
    MovePDFFiles(appConfig.WorkTimePDFPath,appConfig.PDFSavePath)
    logger.info("完成存档")

def sanitize_windows_filename(filename):
    # 删除非法字符和控制字符（ASCII 0-31）
    cleaned = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '', filename)
    
    # 去除开头和结尾的空格和点
    cleaned = re.sub(r'^[ .]+', '', cleaned)    # 开头
    cleaned = re.sub(r'[ .]+$', '', cleaned)     # 结尾
    
    # 替换连续空格为单个空格
    cleaned = re.sub(r' +', ' ', cleaned)
    
    # 处理空文件名
    if not cleaned:
        cleaned = "unnamed_file"
    
    # 处理保留名称（如 CON, PRN 等）
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL', 
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    if cleaned.upper() in reserved_names:
        cleaned += '_'
    
    return cleaned