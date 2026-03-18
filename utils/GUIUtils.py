import pyautogui
import pyperclip
import config.appConfig as appConfig
from datetime import datetime
from PIL import ImageGrab
pyautogui.FAILSAFE = False

def clickByImg(logger,img_path,offsetx,offsety,confi):
    
    target_position = pyautogui.locateCenterOnScreen(img_path,confidence=confi)

    if target_position is not None:
        # 获取偏移量
        offset_x = offsetx
        offset_y = offsety

        # 计算实际点击位置
        click_x = target_position.x + offset_x
        click_y = target_position.y + offset_y

        # 点击指定位置
        pyautogui.click(click_x, click_y)
        
    else:
        screenShoot(img_path)
        logger.info("未找到指定图片:"+img_path)

def DoubleclickByImg(logger,img_path,offsetx,offsety,confi):
    
    target_position = pyautogui.locateCenterOnScreen(img_path,confidence=confi)

    if target_position is not None:
        # 获取偏移量
        offset_x = offsetx
        offset_y = offsety

        # 计算实际点击位置
        click_x = target_position.x + offset_x
        click_y = target_position.y + offset_y

        # 点击指定位置
        pyautogui.doubleClick(click_x, click_y)
        
    else:
        screenShoot(img_path)
        logger.info("未找到指定图片:"+img_path)


def rightClickByImg(logger,img_path,offsetx,offsety,confi):
    
    target_position = pyautogui.locateCenterOnScreen(img_path,confidence=confi)

    if target_position is not None:
        # 获取偏移量
        offset_x = offsetx
        offset_y = offsety

        # 计算实际点击位置
        click_x = target_position.x + offset_x
        click_y = target_position.y + offset_y

        # 点击指定位置
        pyautogui.rightClick(click_x, click_y)
        
    else:
        screenShoot(img_path)
        logger.info("未找到指定图片:"+img_path)



import time
import pyautogui

# 等待元素出现
def waitUntilShow(logger,imgPath, timeout=20,Shoot = True):
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # 尝试在屏幕上定位图片
            position = pyautogui.locateOnScreen(image=imgPath,grayscale=False,confidence=0.9)
            if position:
                # 如果找到图片，退出循环
                logger.info(f"Image postion:{imgPath}:{position.left}, {position.top}")
                return pyautogui.center(position)
                break
            else:
                # 如果没有找到图片，继续循环
                logger.info(f"Image not found !{imgPath}: waiting ...")
                time.sleep(0.1)  # 等待1秒
        # except pyautogui.ImageNotFoundException:
        except Exception as e:
            logger.info(f"Image not found :{imgPath} " + str(time.time() - start_time) +f"Exception:{e}")
            time.sleep(0.1)  # 等待1秒
    else:
        if(Shoot == True):
            screenShoot(imgPath)
            # 如果超出了超时时间，则元素未找到
            logger.info(f"超时未找到图像:{imgPath}")

def wait_for_image_to_disappear(logger,image_path, confidence=0.9, interval=0.01):
    while True:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location is None:
            logger.info(f"Image not found !{image_path}: next ...")
            break
        time.sleep(interval)
        logger.info(f"Image found !{image_path}: waiting ...")

# 点击元素    
def click(imgPath):
    pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(image=imgPath,grayscale=False,confidence=0.9)))

# 点击元素直至元素出现
def clickUntilShow(logger,img_path,offsetx,offsety,confi,wait_imgPath,timeout):
    position = waitUntilShow(logger,wait_imgPath,timeout)
    if position:
        clickByImg(logger,img_path,offsetx,offsety,confi)
        return True
    else:
        screenShoot(wait_imgPath)
        return False

# 等到元素出现回车
def enterUntilShow(logger,wait_imgPath,timeout):
    position = waitUntilShow(logger,wait_imgPath,timeout)
    if position:
        pyautogui.press("enter")
        return True
    else:
        screenShoot(wait_imgPath)
        return False

# 等到元素出现回车
def typeWritewithShiftUntilShow(logger,text,wait_imgPath,timeout):
    position = waitUntilShow(logger,wait_imgPath,timeout)
    if position:
        time.sleep(1)
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl','v')
        return True
    else:
        screenShoot(wait_imgPath)
        return False   

# 等到元素出现最大化窗口 
def maxWindowUntilShow(logger,wait_imgPath,timeout):
    position = waitUntilShow(logger,wait_imgPath,timeout)
    if position:
        pyautogui.hotkey('winleft','up')
        return True
    else:
        screenShoot(wait_imgPath)
        return False
    
def ShowMessageBox():
    
    starttime = ''
    endtime = ''
    res = pyautogui.confirm(text='是否需要手动出库？', title='出库修复程序', buttons=['需要', '取消'])

    if(res == '需要'):
        next = pyautogui.confirm(text='需要做KA5还是只要销账', title='出库修复程序', buttons=['KA5','销账', '取消'])
        if next == 'KA5':
            starttime = pyautogui.prompt(text='只可以输入今天或者昨天的时间\r输入开始日期\r格式样例：【1900-01-01 01:01:01】', title='出库修复程序', default='')
            if is_date_format(starttime):
                endtime = pyautogui.prompt(text='只可以输入今天或者昨天的时间\r输入结束日期\r格式样例：【1900-01-01 01:01:01】', title='出库修复程序', default='')
                if is_date_format(endtime):
                    res = pyautogui.confirm(text='请确认是否是如下数据\r开始时间：'+starttime+"\r结束时间："+endtime, title='出库修复程序', buttons=['确定', '取消'])
                    if res == '确定':
                        return next,starttime,endtime
                else:
                    res = pyautogui.confirm(text='停止出库,请确认输入格式', title='出库修复程序', buttons=['确定'])
                    return '取消','',''
            else:
                res = pyautogui.confirm(text='停止出库,请确认输入格式', title='出库修复程序', buttons=['确定'])
                return '取消','',''
        elif next == '销账':
            res = pyautogui.confirm(text='销昨天和今天的帐', title='出库修复程序', buttons=['确定'])
            return next,'',''
    else:
        return res,'',''

def ShowWrite_OFF_ERROR():
    pyautogui.confirm(text='没有需要销账项', title='出库修复程序', buttons=['确定', '取消'])

def Show_Alert():
    pyautogui.alert(text='RPA程序即将启动\r请确认键盘大写灯熄灭 输入法为英文 \r准备结束 \r点击确定后请勿对电脑有任何操作', title='出库修复程序', button='确定')

def Show_AlertWithMsg(txt):
    pyautogui.alert(text=txt, title='出库修复程序', button='确定')

def is_date_format(string):
    try:
        datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        return True
    except Exception as e:
        return False
    

def screenShoot(wait_imgPath):
    if 'ERROR' not in wait_imgPath:
        screenshot = ImageGrab.grab()
        path = appConfig.ScreenShootPath +'\\' + wait_imgPath.rsplit('\\', 1)[-1].replace('.png','') + datetime.now().strftime("%Y%m%d%H%M%S") + '.png'
        screenshot.save(path)

def screenShootERROR(wait_imgPath):
    
    screenshot = ImageGrab.grab()
    path = appConfig.ScreenShootPath +'\\' + wait_imgPath.rsplit('\\', 1)[-1].replace('.png','') + datetime.now().strftime("%Y%m%d%H%M%S") + '.png'
    screenshot.save(path)