import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

class Boss直聘自动化:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.职位列表 = []
        
    def 初始化浏览器(self):
        """初始化Chrome浏览器 - 修复data:问题核心版本"""
        options = webdriver.ChromeOptions()
        
        # 基础反检测配置
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # ==============================================
        # 核心修复: 解决data:页面问题
        # ==============================================
        options.add_argument("--no-first-run")                  # 禁用首次运行向导
        options.add_argument("--no-default-browser-check")      # 禁用默认浏览器检查
        options.add_argument("--disable-search-engine-choice-screen")  # 禁用搜索引擎选择
        options.add_argument("--disable-popup-blocking")        # 禁用弹窗拦截
        options.add_argument("--disable-extensions")            # 禁用扩展
        options.add_argument("--disable-plugins")               # 禁用插件
        options.add_argument("--no-sandbox")                    # 禁用沙箱
        
        # 关键修复：使用固定的用户配置目录
        配置目录 = os.path.join(os.path.expanduser("~"), "Boss直聘浏览器配置")
        if not os.path.exists(配置目录):
            os.makedirs(配置目录, exist_ok=True)
        options.add_argument(f"--user-data-dir={配置目录}")
        
        # 禁用各种提示
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,  # 禁用通知
            "credentials_enable_service": False,                       # 禁用密码服务
            "profile.password_manager_enabled": False,                 # 禁用密码管理
            "profile.exit_type": "Normal",                            # 正常退出
            "session.restore_on_startup": 0,                          # 不恢复上次会话
        })
        
        print("正在启动Chrome浏览器...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # 绕过反爬检测
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome浏览器启动成功")
        
    def 检查并修复无效页面(self):
        """检查并修复data:或about:blank页面"""
        try:
            当前地址 = self.driver.current_url
            if "data:" in 当前地址 or "about:blank" in 当前地址 or len(当前地址) < 10:
                print(f"检测到无效页面 [{当前地址}]，正在修复...")
                # 终极修复方案：CDP命令导航
                self.driver.execute_cdp_cmd("Page.navigate", {"url": "https://www.zhipin.com/"})
                time.sleep(3)
                return True
            elif "zhipin" in 当前地址:
                return False
            else:
                print(f"当前页面: {当前地址}")
                return False
        except Exception as e:
            print(f"检查页面出错: {e}")
            return True
            
    def 打开Boss直聘(self):
        """打开Boss直聘网站"""
        print("\n正在打开Boss直聘网站...")
        
        # 策略：先访问一个无害的页面进行初始化
        self.driver.execute_cdp_cmd("Page.navigate", {"url": "about:blank"})
        time.sleep(1)
        
        # 然后访问目标网站
        self.driver.execute_cdp_cmd("Page.navigate", {"url": "https://www.zhipin.com/"})
        time.sleep(3)
        
        # 检查并修复
        if self.检查并修复无效页面():
            time.sleep(2)
            
        print(f"当前地址: {self.driver.current_url}")
        print(f"页面标题: {self.driver.title}")
        print("Boss直聘网站已打开")
        
    def 等待登录(self):
        """等待用户登录"""
        print("\n" + "="*50)
        print("【重要】请完成以下登录步骤：")
        print("1. 在浏览器中点击右上角'登录'按钮")
        print("2. 使用Boss直聘APP扫码完成登录")
        print("3. 登录成功后，请回到这里按回车键继续")
        print("="*50)
        input("登录完成后按回车键继续 >>> ")
        
        # 再次检查页面有效性
        self.检查并修复无效页面()
        print("已确认登录，继续执行任务...")
        
    def 搜索职位(self, 关键词="开发者", 城市="苏州"):
        """搜索职位"""
        try:
            print(f"\n开始搜索: 城市={城市}, 关键词={关键词}")
            
            self.检查并修复无效页面()
            
            # 切换城市
            self.切换城市(城市)
            
            # 输入搜索关键词
            搜索框 = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input, input[placeholder*='搜索']"))
            )
            搜索框.clear()
            搜索框.send_keys(关键词)
            time.sleep(1)
            
            # 点击搜索按钮
            搜索按钮 = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-btn"))
            )
            搜索按钮.click()
            time.sleep(3)
            
            self.检查并修复无效页面()
            print("搜索完成")
            
        except Exception as e:
            print(f"搜索出错: {e}")
            
    def 切换城市(self, 目标城市):
        """切换城市"""
        try:
            城市按钮 = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.city-select, span.city-name"))
            )
            当前城市 = 城市按钮.text.strip()
            print(f"当前城市: {当前城市}")
            
            if 当前城市 == 目标城市:
                return
                
            城市按钮.click()
            time.sleep(1)
            
            # 选择目标城市
            城市列表 = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a")
            for 城市 in 城市列表:
                if 城市.text.strip() == 目标城市:
                    城市.click()
                    print(f"已切换到: {目标城市}")
                    time.sleep(2)
                    return
                    
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def 设置筛选条件(self):
        """设置筛选条件: 全职、薪资10k-13k、公司规模100-10000人"""
        try:
            print("\n正在设置筛选条件...")
            
            self.检查并修复无效页面()
            
            # 1. 选择全职
            try:
                全职按钮 = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='全职']/parent::a | //a[text()='全职']"))
                )
                全职按钮.click()
                print("已筛选: 全职")
            except:
                print("全职筛选设置跳过")
            
            time.sleep(1)
            
            # 2. 设置公司规模
            try:
                规模下拉 = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'filter-select') and contains(., '规模')]"))
                )
                规模下拉.click()
                time.sleep(1)
                
                规模选项 = self.driver.find_elements(
                    By.XPATH, "//ul/li[contains(text(), '100-') or contains(text(), '500-') or contains(text(), '1000-')]"
                )
                for 选项 in 规模选项:
                    选项.click()
                    print(f"已选规模: {选项.text.strip()}")
                    time.sleep(0.3)
            except:
                print("公司规模筛选设置跳过")
                
        except Exception as e:
            print(f"设置筛选条件出错: {e}")
            
    def 收集职位信息(self, 最大数量=10):
        """收集职位信息"""
        print(f"\n正在收集职位信息（最多{最大数量}条）...")
        
        try:
            self.检查并修复无效页面()
            
            职位卡片列表 = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box"))
            )
            
            if not 职位卡片列表:
                print("未找到职位列表")
                return
                
            print(f"当前页面找到 {len(职位卡片列表)} 个职位")
            
            已收集 = 0
            for i, 卡片 in enumerate(职位卡片列表):
                if 已收集 >= 最大数量:
                    break
                    
                try:
                    职位名称 = 卡片.find_element(By.CSS_SELECTOR, "div.job-title a").text.strip()
                    薪资 = 卡片.find_element(By.CSS_SELECTOR, "div.job-title span").text.strip()
                    公司名称 = 卡片.find_element(By.CSS_SELECTOR, "div.company-info a").text.strip()
                    
                    # 地点信息
                    地点列表 = 卡片.find_elements(By.CSS_SELECTOR, "div.job-tag span")
                    地点 = 地点列表[0].text.strip() if 地点列表 else "未知"
                    
                    print(f"{已收集+1}. {职位名称} - {公司名称} - {薪资} - {地点}")
                    
                    # 检查薪资范围（10k-13k）
                    if self.检查薪资范围(薪资):
                        self.职位列表.append({
                            "职位名称": 职位名称,
                            "公司名称": 公司名称,
                            "薪资范围": 薪资,
                            "工作地点": 地点,
                            "备注": "薪资符合10k-13k范围"
                        })
                        已收集 += 1
                    else:
                        print(f"   → 薪资不在目标范围内，跳过")
                    
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
                # 只要有重叠就算符合
                return (最低薪资 <= 13000 and 最高薪资 >= 10000)
            return False
        except:
            return False
            
    def 导出Excel(self, 文件名="苏州_开发者_职位汇总.xlsx"):
        """导出数据到Excel"""
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
        """主运行流程"""
        try:
            print("="*50)
            print("Boss直聘职位搜索自动化工具")
            print("="*50)
            
            # 1. 初始化浏览器
            self.初始化浏览器()
            
            # 2. 打开网站
            self.打开Boss直聘()
            
            # 3. 等待登录
            self.等待登录()
            
            # 4. 搜索职位
            self.搜索职位()
            
            # 5. 设置筛选条件
            self.设置筛选条件()
            
            # 6. 收集职位信息
            self.收集职位信息()
            
            # 7. 导出Excel
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
