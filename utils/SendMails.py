import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def SendEmail(subject,content,PDFPath,FileList=[]):
    # 发件人和收件人信息
    sender_email = "dsz.rpa@daikin.net.cn"
    receiver_email = "yang.junjun@daikin.net.cn"
    password = ""

    # 创建邮件
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    # 添加邮件正文
    message.attach(MIMEText(content, "plain"))
    if(PDFPath != ''):
        if PDFPath != '':
            for file in os.listdir(PDFPath):
                    if os.path.isfile(PDFPath + '/' + file):
                        # 构造附件
                        att = MIMEText(open(PDFPath + '/' + file.replace('~$',''), 'rb').read(), 'base64', 'utf-8')
                        att["Content-Type"] = 'application/octet-stream'
                        att.add_header("Content-Disposition", "attachment", filename=("gbk", "", file))
                        message.attach(att)     
    
    if(len(FileList) > 0):
        if len(FileList) > 0:
            for file in FileList:
                    if os.path.isfile(file):
                        # 构造附件
                        att = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
                        att["Content-Type"] = 'application/octet-stream'
                        att.add_header("Content-Disposition", "attachment", filename=("gbk", "", file))
                        message.attach(att)

    # 连接到SMTP服务器
    with smtplib.SMTP("smtp.daikin.net.cn", 25) as server:
        server.starttls()
        # server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("邮件已发送成功！")
