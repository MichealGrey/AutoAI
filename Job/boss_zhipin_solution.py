import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

class BossZhipinAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.jobs_data = []
        
    def init_driver(self):
        """初始化Chrome - 解决data:问题的关键配置"""
        options = webdriver.ChromeOptions()
        
        # 基础配置
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 关键修复: 解决data:问题
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-search-engine-choice-screen")
        options.add_argument("--disable-popup-blocking")
        
        # 关键修复: 使用现有配置文件，避免首次启动问题
        user_data_dir = os.path.join(os.path.expanduser("~"), "chrome_profile_boss")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # 禁用首次运行提示
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "exit_type": "Normal"
        })
        
        print("正在启动Chrome浏览器...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # 绕过反爬检测
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome启动完成")
        
    def fix_data_url(self):
        """修复data: URL问题"""
        try:
            current_url = self.driver.current_url
            if "data:" in current_url or "about:blank" in current_url or len(current_url) < 10:
                print("检测到无效页面，正在修复...")
                # 解决方案：执行JavaScript来跳转
                self.driver.execute_script("window.location.href = 'https://www.zhipin.com/';")
                time.sleep(3)
                return True
        except Exception as e:
            print(f"URL修复出错: {e}")
        return False
        
    def open_website(self):
        """打开网站"""
        print("\n正在打开Boss直聘...")
        
        # 先随便访问一个页面触发初始化
        self.driver.get("about:blank")
        time.sleep(1)
        
        # 然后访问目标网站
        self.driver.get("https://www.zhipin.com/")
        time.sleep(3)
        
        # 检查并修复data:问题
        self.fix_data_url()
        
        # 双重检查
        current_url = self.driver.current_url
        print(f"当前页面: {current_url}")
        
        if "zhipin.com" not in current_url:
            print("尝试第二次加载...")
            self.driver.get("https://www.zhipin.com/")
            time.sleep(3)
            self.fix_data_url()
            
        print(f"页面标题: {self.driver.title}")
        print("网站加载完成")
        
    def wait_for_login(self):
        """等待登录"""
        print("\n" + "="*50)
        print("登录步骤:")
        print("1. 在浏览器中点击右上角'登录'")
        print("2. 使用Boss直聘APP扫码")
        print("3. 登录成功后按回车继续")
        print("="*50)
        input("登录完成后按回车键 >>> ")
        
        # 确保页面正确
        self.fix_data_url()
        print("继续执行...")
        
    def search_jobs(self, keyword="开发者", city="苏州"):
        """搜索职位"""
        try:
            print(f"\n搜索: {city} {keyword}")
            
            # 确保页面正确
            self.fix_data_url()
            
            # 切换城市
            self._switch_city(city)
            
            # 输入关键词
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input, input[placeholder*='搜索']"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(1)
            
            # 点击搜索
            search_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-btn"))
            )
            search_btn.click()
            time.sleep(3)
            
            # 再次检查data:问题
            self.fix_data_url()
            print("搜索完成")
            
        except Exception as e:
            print(f"搜索出错: {e}")
            
    def _switch_city(self, target_city):
        """切换城市"""
        try:
            city_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.city-select, span.city-name"))
            )
            current_city = city_btn.text.strip()
            
            if current_city == target_city:
                print(f"当前城市: {current_city}")
                return
                
            city_btn.click()
            time.sleep(1)
            
            # 选择城市
            city_links = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a")
            for link in city_links:
                if link.text.strip() == target_city:
                    link.click()
                    print(f"已切换到: {target_city}")
                    time.sleep(2)
                    return
                    
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def set_filters(self):
        """设置筛选条件"""
        try:
            print("\n设置筛选条件...")
            self.fix_data_url()
            
            # 选择全职
            try:
                fulltime = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='全职']/parent::a"))
                )
                fulltime.click()
                print("已选: 全职")
            except:
                pass
                
            time.sleep(1)
            
        except Exception as e:
            print(f"设置筛选出错: {e}")
            
    def collect_jobs(self):
        """收集职位"""
        print("\n收集职位信息...")
        
        try:
            self.fix_data_url()
            
            job_cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box"))
            )
            
            print(f"找到 {len(job_cards)} 个职位")
            
            for i, card in enumerate(job_cards[:10]):
                try:
                    title = card.find_element(By.CSS_SELECTOR, "div.job-title a").text.strip()
                    salary = card.find_element(By.CSS_SELECTOR, "div.job-title span").text.strip()
                    company = card.find_element(By.CSS_SELECTOR, "div.company-info a").text.strip()
                    
                    print(f"{i+1}. {title} - {company} - {salary}")
                    
                    self.jobs_data.append({
                        "职位名称": title,
                        "公司名称": company,
                        "薪资范围": salary
                    })
                    
                except Exception as e:
                    print(f"处理职位{i+1}出错: {e}")
                    continue
                    
        except Exception as e:
            print(f"收集出错: {e}")
            
    def export_excel(self):
        """导出Excel"""
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            df.to_excel("职位汇总.xlsx", index=False, engine="openpyxl")
            print(f"\n导出成功！文件: 职位汇总.xlsx")
            print(f"共 {len(self.jobs_data)} 条记录")
        else:
            print("\n没有数据可导出")
            
    def run(self):
        """主流程"""
        try:
            print("="*50)
            print("Boss直聘职位搜索工具")
            print("="*50)
            
            # 初始化
            self.init_driver()
            
            # 打开网站
            self.open_website()
            
            # 等待登录
            self.wait_for_login()
            
            # 搜索
            self.search_jobs()
            
            # 筛选
            self.set_filters()
            
            # 收集
            self.collect_jobs()
            
            # 导出
            self.export_excel()
            
            print("\n任务完成！")
            
        except Exception as e:
            print(f"\n出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            input("\n按回车键关闭浏览器...")
            if self.driver:
                self.driver.quit()
                print("浏览器已关闭")

if __name__ == "__main__":
    app = BossZhipinAutomation()
    app.run()
