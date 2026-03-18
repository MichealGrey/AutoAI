import os



def kill_CMD():
    '''杀CMD进程'''
    #根据进程名杀死进程
    pro = 'taskkill /f /im cmd.exe'
    os.system(pro)

def kill_Alpha():
    '''杀ALPHA进程'''
    #根据进程名杀死进程
    pro = 'taskkill /f /im GenTabMenu.exe'
    os.system(pro)

def kill_Chrome():
    '''杀Chrome进程'''
    #根据进程名杀死进程
    pro = 'taskkill /f /im chrome.exe'
    os.system(pro)

def kill_KA7():
    '''杀KA7进程'''
    #根据进程名杀死进程
    pro = 'taskkill /f /im GenTabSvrDB2.exe'
    os.system(pro)

def kill_KA8():
    '''杀KA8进程'''
    #根据进程名杀死进程
    pro = 'taskkill /f /im GSB_BSK02400.exe'
    os.system(pro)

def kill_KA5():
    '''杀KA5进程'''
    #根据进程名杀死进程
    pro = 'taskkill /f /im GSB_BSK02300.exe'
    os.system(pro)

def kill_EXCEL():
    '''杀EXCEL进程'''
    #根据进程名杀死进程
    pro = 'taskkill /f /im EXCEL.EXE'
    os.system(pro)

def seconds_to_hms(seconds):
    hours = seconds // 3600
    remainder = seconds % 3600
    minutes, seconds = seconds_to_hms_helper(remainder)
    return hours, minutes, seconds
 
def seconds_to_hms_helper(seconds):
    if seconds < 60:
        return 0, seconds
    minutes = seconds // 60
    seconds = seconds % 60
    return minutes, seconds

def kill_APPS():
    kill_Alpha()
    kill_CMD()
    kill_Chrome()
    kill_KA5()
    kill_KA7()
    kill_KA8()
    kill_EXCEL()
