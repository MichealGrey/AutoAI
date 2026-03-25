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
        self.主窗口句柄 = None
        self.职位列表 = []
        
    def 初始化浏览器(self):
        """初始化Chrome浏览器 - 最终修复版"""
        options = webdriver.ChromeOptions()
        
        # 基础配置
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 修复配置
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        
        # 关键修复：禁用重定向和弹窗
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.popups": 2,
            "profile.default_content_setting_values.javascript": 1,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.exit_type": "Normal",
        })
        
        print("正在启动Chrome浏览器...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # 绕过反爬检测
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.open = function() { return window; };  // 阻止打开新窗口
            """
        })
        
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome启动完成")
        
    def 阻止新窗口打开(self):
        """注入JS阻止新窗口打开"""
        try:
            self.driver.execute_script("""
                // 阻止window.open
                const originalOpen = window.open;
                window.open = function(url, name, features) {
                    console.log('阻止打开:', url);
                    // 改为在当前窗口跳转
                    if(url) {
                        window.location.href = url;
                    }
                    return window;
                };
                
                // 阻止target="_blank"的链接
                document.addEventListener('click', function(e) {
                    const target = e.target.closest('a');
                    if(target && target.target === '_blank') {
                        target.target = '_self';
                    }
                }, true);
            """)
        except:
            pass
            
    def 保存主窗口(self):
        """保存当前窗口作为主窗口"""
        self.主窗口句柄 = self.driver.current_window_handle
        print(f"主窗口已保存: {self.主窗口句柄[:10]}...")
        
    def 切回主窗口(self):
        """确保在主窗口操作"""
        try:
            # 关闭所有其他窗口
            for handle in self.driver.window_handles:
                if handle != self.主窗口句柄:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                        print(f"关闭额外窗口: {handle[:10]}...")
                    except:
                        pass
                        
            # 切回主窗口
            if self.主窗口句柄 in self.driver.window_handles:
                self.driver.switch_to.window(self.主窗口句柄)
            else:
                # 如果主窗口关闭了，使用第一个可用窗口
                if self.driver.window_handles:
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.主窗口句柄 = self.driver.window_handles[0]
                    
        except Exception as e:
            print(f"切换窗口出错: {e}")
            
    def 打开Boss直聘(self):
        """打开Boss直聘网站 - 修复跳转问题"""
        print("\n正在打开Boss直聘网站...")
        
        # 先打开空白页
        self.driver.get("about:blank")
        time.sleep(1)
        
        # 保存主窗口
        self.保存主窗口()
        
        # 关键修复：使用CDP导航，防止跳转
        self.driver.execute_cdp_cmd("Page.navigate", {
            "url": "https://www.zhipin.com/",
            "transitionType": "typed"
        })
        time.sleep(3)
        
        # 检查并修复窗口问题
        self.切回主窗口()
        
        # 注入JS阻止弹窗
        self.阻止新窗口打开()
        
        # 检查页面
        current_url = self.driver.current_url
        print(f"当前URL: {current_url}")
        print(f"窗口数量: {len(self.driver.window_handles)}")
        
        # 如果还是有跳转问题，尝试二次加载
        if "zhipin.com" not in current_url or len(self.driver.window_handles) > 1:
            print("检测到异常，二次加载...")
            self.切回主窗口()
            self.driver.get("https://www.zhipin.com/")
            time.sleep(3)
            self.阻止新窗口打开()
            
        print(f"页面标题: {self.driver.title}")
        print("Boss直聘网站加载完成")
        
    def 等待登录(self):
        """等待用户登录"""
        print("\n" + "="*50)
        print("【登录操作说明】")
        print("1. 请在浏览器中点击右上角'登录'按钮")
        print("2. 使用Boss直聘APP扫码登录")
        print("3. 登录成功后按回车键继续")
        print("="*50)
        
        # 持续检查窗口状态
        while True:
            self.切回主窗口()
            try:
                current_url = self.driver.current_url
                print(f"\r当前页面: {current_url[:50]}...", end="", flush=True)
            except:
                pass
            time.sleep(1)
            break
            
        input("\n登录完成后按回车键继续 >>> ")
        
        # 再次确保在主窗口
        self.切回主窗口()
        self.阻止新窗口打开()
        print("继续执行任务...")
        
    def 搜索职位(self, 关键词="开发者", 城市="苏州"):
        """搜索职位"""
        try:
            print(f"\n开始搜索: 城市={城市}, 关键词={关键词}")
            
            self.切回主窗口()
            self.阻止新窗口打开()
            
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
            self.driver.execute_script("arguments[0].removeAttribute('target'); arguments[0].click();", 搜索按钮)
            time.sleep(3)
            
            self.切回主窗口()
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
                
            self.driver.execute_script("arguments[0].removeAttribute('target'); arguments[0].click();", 城市按钮)
            time.sleep(1)
            
            # 选择目标城市
            城市列表 = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a")
            for 城市 in 城市列表:
                if 城市.text.strip() == 目标城市:
                    self.driver.execute_script("arguments[0].removeAttribute('target'); arguments[0].click();", 城市)
                    print(f"已切换到: {目标城市}")
                    time.sleep(2)
                    return
                    
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def 设置筛选条件(self):
        """设置筛选条件"""
        try:
            print("\n正在设置筛选条件...")
            
            self.切回主窗口()
            
            # 选择全职
            try:
                全职按钮 = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='全职']/parent::a | //a[text()='全职']"))
                )
                self.driver.execute_script("arguments[0].removeAttribute('target'); arguments[0].click();", 全职按钮)
                print("已筛选: 全职")
            except:
                print("全职筛选设置跳过")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"设置筛选条件出错: {e}")
            
    def 收集职位信息(self, 最大数量=10):
        """收集职位信息"""
        print(f"\n正在收集职位信息（最多{最大数量}条）...")
        
        try:
            self.切回主窗口()
            
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
                    
                    地点列表 = 卡片.find_elements(By.CSS_SELECTOR, "div.job-tag span")
                    地点 = 地点列表[0].text.strip() if 地点列表 else "未知"
                    
                    print(f"{已收集+1}. {职位名称} - {公司名称} - {薪资} - {地点}")
                    
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
            print("Boss直聘职位搜索自动化工具 - 最终修复版")
            print("="*50)
            
            self.初始化浏览器()
            self.打开Boss直聘()
            self.等待登录()
            self.搜索职位()
            self.设置筛选条件()
            self.收集职位信息()
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
