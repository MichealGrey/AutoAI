import requests
import win32com.client
import pandas as pd
import config.appConfig as appConfig
import os 

def Send(message,notify,notifyType,atall):
    notifyUsers = getNotifyUsers(appConfig.WeChatUsersExcel,notifyType)
    send_message(message,notify,notifyUsers,atall)

def Send_ExcuteFiles(sendMailPath):
    files = os.listdir(sendMailPath)
    os.chdir(sendMailPath)

    for file in files:
        media_id = uploadFile(sendMailPath + file)
        send_file(media_id)

def getNotifyUsers(userFilePath,notify):
    df = pd.read_excel(userFilePath)
    fliterdf = df[df['警报等级']==notify]
    return fliterdf['工号'].to_list()


def send_message(message,notify,notifyUsers,atall):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='+ appConfig.WechatwebHook
    
    message_data = {}
    if atall==True:
        message_data = {
            "msgtype": "text",
            "text": {
                "content": message,
                "mentioned_mobile_list":["@all"]
            },
        }
    elif len(notifyUsers) > 0 and notify == True:
        message_data = {
            "msgtype": "text",
            "text": {
                "content": message,
                "mentioned_list":notifyUsers
            },
        }
    else:
        message_data = {
            "msgtype": "text",
            "text": {
                "content": message,
            },
        }
    response = requests.post(url, json=message_data)
    res_data = response.json()
    print(res_data)
    print("finished sending message")

def send_file(media_id):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='+ appConfig.WechatwebHook
    message_data = {
        "msgtype": "file",
        "file": {
 		"media_id": media_id
        }
    }
    response = requests.post(url, json=message_data)
    res_data = response.json()
    print(res_data)
    print("finished sending file")
def uploadFile(file_Path):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key='+ appConfig.WechatwebHook +'&type=file'
    file = {'media': open(file_Path, 'rb')}
    response = requests.post(url, files=file)
    media_id = response.json()['media_id']
    print(f"Uploaded file {file_Path} with media_id {media_id}")
    print("finished")
    return media_id

if __name__ == '__main__':
      
    media_id = uploadFile(r'D:\PythonProject\PyTest\排班.xlsx')
    send_file(media_id)
    send_message("Hello Everyones!")  