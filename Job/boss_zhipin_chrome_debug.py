import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import subprocess
import sys

class Boss直聘自动化:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.职位列表 = []
        
    def 连接到已打开的浏览器(self):
        """连接到已经在调试模式的Chrome"""
        print("="*60)
        print("【重要】请先手动完成以下步骤：")
        print("1. 关闭所有已经打开的Chrome浏览器窗口")
        print("2. 按Win+R组合键打开'运行'对话框")
        print("3. 复制并执行下面这行命令：")
        print('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        print("4. 按Enter运行上面的命令启动Chrome")
        print("="*60)
        input("完成以上步骤后，按Enter键开始连接 >>> ")
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        print("正在连接到Chrome...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 20)
        print("连接成功！")
        return True
        
    def 打开Boss直聘(self):
        print("\n正在打开Boss直聘...")
        # 直接在当前标签页导航
        if self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        self.driver.get("https://www.zhipin.com/")
        time.sleep(3)
        
        print(f"当前URL: {self.driver.current_url}")
        print("网站加载完成")
        
    def 等待登录(self):
        print("\n" + "="*50)
        print("请在浏览器中完成登录：")
        print("1. 点击右上角'登录'按钮")
        print("2. 使用Boss直聘APP扫码")
        print("="*50)
        input("登录完成后按Enter键继续 >>> ")
        
    def 搜索职位(self, 关键词="开发者", 城市="苏州"):
        try:
            print(f"\n开始搜索: {城市} {关键词}")
            
            # 切换城市
            self.切换城市(城市)
            
            # 输入关键词
            搜索框 = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input"))
            )
            搜索框.clear()
            搜索框.send_keys(关键词)
            time.sleep(1)
            
            # 点击搜索
            搜索按钮 = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-btn"))
            )
            搜索按钮.click()
            time.sleep(3)
            
            print("搜索完成")
            
        except Exception as e:
            print(f"搜索出错: {e}")
            
    def 切换城市(self, 目标城市):
        try:
            城市按钮 = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.city-select"))
            )
            当前城市 = 城市按钮.text.strip()
            print(f"当前城市: {当前城市}")
            
            if 当前城市 == 目标城市:
                return
                
            城市按钮.click()
            time.sleep(1)
            
            # 选择城市
            城市列表 = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a")
            for 城市 in 城市列表:
                if 城市.text.strip() == 目标城市:
                    城市.click()
                    print(f"已切换到: {目标城市}")
                    time.sleep(2)
                    return
                    
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def 收集职位信息(self, 最大数量=10):
        print(f"\n收集职位信息...")
        
        try:
            职位卡片列表 = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box"))
            )
            
            print(f"找到 {len(职位卡片列表)} 个职位")
            
            for i, 卡片 in enumerate(职位卡片列表[:最大数量]):
                try:
                    职位名称 = 卡片.find_element(By.CSS_SELECTOR, "div.job-title a").text.strip()
                    薪资 = 卡片.find_element(By.CSS_SELECTOR, "div.job-title span").text.strip()
                    公司名称 = 卡片.find_element(By.CSS_SELECTOR, "div.company-info a").text.strip()
                    
                    print(f"{i+1}. {职位名称} - {公司名称} - {薪资}")
                    
                    地点列表 = 卡片.find_elements(By.CSS_SELECTOR, "div.job-tag span")
                    地点 = 地点列表[0].text.strip() if 地点列表 else "未知"
                    
                    if self.检查薪资范围(薪资):
                        self.职位列表.append({
                            "职位名称": 职位名称,
                            "公司名称": 公司名称,
                            "薪资范围": 薪资,
                            "工作地点": 地点
                        })
                    
                except Exception as e:
                    print(f"处理第{i+1}个职位出错: {e}")
                    continue
                    
            print(f"\n收集完成，共收集 {len(self.职位列表)} 条符合条件的记录")
            
        except Exception as e:
            print(f"收集职位出错: {e}")
            
    def 检查薪资范围(self, 薪资文本):
        """检查薪资是否在10k-13k范围内"""
        try:
            薪资文本 = 薪资文本.upper().replace("K", "000")
            if "-" in 薪资文本:
                最低, 最高 = 薪资文本.split("-", 1)
                最低薪资 = int(''.join(filter(str.isdigit, 最低)))
                最高薪资 = int(''.join(filter(str.isdigit, 最高.split()[0])))
                return (最低薪资 <= 13000 and 最高薪资 >= 10000)
        except:
            return False
            
    def 导出Excel(self, 文件名="苏州_开发者_职位汇总.xlsx"):
        if self.职位列表:
            df = pd.DataFrame(self.职位列表)
            df.to_excel(文件名, index=False, engine="openpyxl")
            完整路径 = os.path.abspath(文件名)
            print(f"\n{'='*50}")
            print(f"✓ 数据导出成功！")
            print(f"文件位置: {完整路径}")
            print(f"记录数量: {len(self.职位列表)} 条")
            print(f"{'='*50}")
        else:
            print("\n未找到符合条件的职位数据")
            
    def 运行(self):
        try:
            print("="*50)
            print("Boss直聘职位搜索 - Chrome调试连接版")
            print("="*50)
            
            # 连接浏览器
            if not self.连接到已打开的浏览器():
                return
                
            # 打开网站
            self.打开Boss直聘()
            
            # 等待登录
            self.等待登录()
            
            # 搜索职位
            self.搜索职位()
            
            # 收集职位信息
            self.收集职位信息()
            
            # 导出Excel
            self.导出Excel()
            
            print("\n任务执行完成！")
            
        except Exception as e:
            print(f"\n执行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            input("\n按回车键关闭浏览器并退出程序...")
            if self.driver:
                self.driver.quit()
                print("浏览器已关闭")

if __name__ == "__main__":
    工具 = Boss直聘自动化()
    工具.运行()
