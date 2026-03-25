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
        self.主窗口 = None
        self.职位列表 = []
        
    def 初始化浏览器(self):
        """终极版：使用DevTools协议拦截弹窗"""
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
        
        # 关键：使用DevTools协议拦截窗口创建
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.popups": 2,
            "profile.default_content_setting_values.javascript": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        })
        
        print("正在启动Chrome浏览器...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # 启用CDP事件监听
        self.driver.execute_cdp_cmd("Page.enable", {})
        self.driver.execute_cdp_cmd("Network.enable", {})
        
        # 关键：拦截窗口打开事件
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                
                // 完全禁用window.open
                const realWindowOpen = window.open;
                window.open = function(url, name, specs) {
                    console.log('[拦截] 尝试打开新窗口:', url);
                    if (url && url.includes('zhipin')) {
                        console.log('[重定向到当前页');
                        window.location.href = url;
                    }
                    return window;
                };
                
                // 禁用target=_blank修复
                document.addEventListener('click', (e) => {
                    let target = e.target;
                    while(target) {
                        if(target.tagName === 'A' && target.target === '_blank') {
                            console.log('[拦截] 链接的target="_blank"');
                            target.target = '_self';
                        }
                        target = target.parentElement;
                    }
                }, true);
                
                // 禁用表单的target="_blank"
                document.addEventListener('submit', (e) => {
                    if(e.target.target === '_blank') {
                        console.log('[拦截] 表单的target="_blank"');
                        e.target.target = '_self';
                    }
                }, true);
            """
        })
        
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome启动完成")
        
    def 保存主窗口(self):
        """保存当前窗口为主窗口"""
        self.主窗口 = self.driver.current_window_handle
        print(f"主窗口句柄已保存")
        
    def 清理额外窗口(self):
        """强制清理所有额外窗口"""
        try:
            all_handles = self.driver.window_handles
            if len(all_handles) > 1:
                print(f"发现 {len(all_handles)} 个窗口，正在清理...")
                for handle in all_handles:
                    if handle != self.主窗口:
                        try:
                            self.driver.switch_to.window(handle)
                            url = self.driver.current_url
                            print(f"  关闭窗口:", url[:30:], "...")
                            self.driver.close()
                        except:
                            pass
                # 切回主窗口
                if self.主窗口 in self.driver.window_handles:
                    self.driver.switch_to.window(self.主窗口)
                else:
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.主窗口 = self.driver.window_handles[0]
                print("已完成，剩余窗口数:", len(self.driver.window_handles))
        except Exception as e:
            print(f"清理窗口出错: {e}")
            
    def CDP方式打开网页(self, url):
        """使用CDP方式导航，最底层调用框架"""
        # 直接使用CDP方式打开网页，底层调用框架
        self.driver.execute_cdp_cmd("Page.navigate", {"url": "about:blank})
        time.sleep(1)
        
        self.保存主窗口()
        
        # 使用最可靠的方式导航
        self.driver.execute_cdp_cmd("Page.navigate", {"url": url})
        time.sleep(3)
        
        # 立即清理
        self.清理额外窗口()
        self.driver.switch_to.window(self.主窗口)
        
    def 打开Boss直聘(self):
        print("\n正在打开Boss直聘网站...")
        self.CDP方式打开网页("https://www.zhipin.com/")
        
        # 持续监测并清理
        for i in range(3):
            time.sleep(1)
            self.清理额外窗口()
            
        print(f"当前URL: {self.driver.current_url}")
        print(f"窗口数量: {len(self.driver.window_handles)}")
        print("网站加载完成")
        
    def 等待登录(self):
        print("\n" + "="*50)
        print("【请在浏览器中完成登录】")
        print("1. 点击右上角'登录'按钮")
        print("2. 使用Boss直聘APP扫码登录")
        print("3. 登录成功后按回车继续")
        print("="*50)
        
        # 后台监测窗口
        while True:
            self.清理额外窗口()
            try:
                print(f"\r当前页面: {self.driver.current_url[:40]}...", end="", flush=True)
            except:
                pass
            time.sleep(1)
            break
            
        input("\n登录完成后按回车键继续 >>> ")
        
        self.清理额外窗口()
        print("\n继续执行任务...")
        
    def 搜索职位(self, 关键词="开发者", 城市="苏州"):
        try:
            print(f"\n搜索职位: {城市} {关键词}")
            self.清理额外窗口()
            
            self.切换城市(城市)
            
            搜索框 = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input"))
            搜索框.clear()
            搜索框.send_keys(关键词)
            time.sleep(1)
            
            搜索按钮 = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-btn"))
            self.driver.execute_script("arguments[0].target='_self'; arguments[0].click();", 搜索按钮)
            time.sleep(3)
            
            self.清理额外窗口()
            print("搜索完成")
            
        except Exception as e:
            print(f"搜索出错: {e}")
            
    def 切换城市(self, 目标城市):
        try:
            城市按钮 = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.city-select"))
            当前城市 = 城市按钮.text.strip()
            print(f"当前城市: {当前城市}")
            
            if 当前城市 == 目标城市:
                return
                
            self.driver.execute_script("arguments[0].target='_self'; arguments[0].click();", 城市按钮)
            time.sleep(1)
            
            城市列表 = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a")
            for 城市 in 城市列表:
                if 城市.text.strip() == 目标城市:
                    self.driver.execute_script("arguments[0].target='_self'; arguments[0].click();", 城市)
                    print(f"已切换到城市: {目标城市}")
                    time.sleep(2)
                    return
                    
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def 设置筛选条件(self):
        try:
            print("\n设置筛选条件...")
            self.清理额外窗口()
            
            try:
                全职按钮 = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='全职']/parent::a")))
                self.driver.execute_script("arguments[0].target='_self'; arguments[0].click();", 全职按钮)
                print("已选: 全职")
            except:
                pass
                
        except Exception as e:
            print(f"设置筛选出错: {e}")
            
    def 收集职位信息(self, 最大数量=10):
        print(f"\n收集职位信息(最多{最大数量}条)")
        
        try:
            self.清理额外窗口()
            
            职位卡片 = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box"))
            
            print(f"找到 {len(职位卡片)} 个职位")
            
            for i, 卡片 in enumerate(职位卡片[:最大数量)):
                try:
                    职位名称 = 卡片.find_element(By.CSS_SELECTOR, "div.job-title a").text.strip()
                    薪资 = 卡片.find_element(By.CSS_SELECTOR, "div.job-title span").text.strip()
                    公司名称 = 卡片.find_element(By.CSS_SELECTOR, "div.company-info a").text.strip()
                    
                    print(f"{i+1}. {职位名称} - {公司名称} - {薪资}")
                    
                    if self.检查薪资范围(薪资):
                        self.职位列表.append({"职位名称": 职位名称, "公司名称": 公司名称, "薪资范围": 薪资})
                    
                except Exception as e:
                    print(f"处理出错: {e}")
                    continue
                    
            print(f"收集完成，共 {len(self.职位列表)} 条符合条件")
            
        except Exception as e:
            print(f"收集职位出错: {e}")
            
    def 检查薪资范围(self, 薪资文本):
        try:
            薪资文本 = 薪资文本.upper().replace("K", "000")
            if "-" in 薪资文本:
                最低, 最高 = 薪资文本.split("-", 1)
                最低薪资 = int(''.join(filter(str.isdigit, 最低))
                最高薪资 = int(''.join(filter(str.isdigit, 最高.split()[0]))
                return 最低薪资 <= 13000 and 最高薪资 >= 10000
        except:
            return False
            
    def 导出Excel(self):
        if self.职位列表:
            df = pd.DataFrame(self.职位列表)
            df.to_excel("职位汇总.xlsx", index=False, engine="openpyxl")
            print(f"\n导出成功！共 {len(self.职位列表)} 条记录")
        else:
            print("\n没有数据")
            
    def 运行(self):
        try:
            print("="*50)
            print("Boss直聘终极版")
            print("="*50)
            
            self.初始化浏览器()
            self.打开Boss直聘()
            self.等待登录()
            self.搜索职位()
            self.设置筛选条件()
            self.收集职位信息()
            self.导出Excel()
            
            print("\n任务完成！")
            
        except Exception as e:
            print(f"\n出错: {e}")
        finally:
            input("\n按回车退出...")
            self.driver.quit()

if __name__ == "__main__":
    app = Boss直聘自动化()
    app.运行()
