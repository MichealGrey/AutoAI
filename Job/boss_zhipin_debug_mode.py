import time
import pandas as pd
import subprocess
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class BossZhipinAutomation:
    def __init__(self, debug_port=9222):
        self.driver = None
        self.wait = None
        self.debug_port = debug_port
        self.jobs_data = []
        self.chrome_process = None
        
    def _get_chrome_path(self):
        """获取Chrome路径"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
        
    def _start_chrome_with_debug(self):
        """以调试模式启动Chrome"""
        chrome_path = self._get_chrome_path()
        if not chrome_path:
            raise Exception("未找到Chrome浏览器，请确认已安装Chrome")
            
        # 确保用户数据目录
        user_data_dir = os.path.join(os.path.expanduser("~"), "chrome_boss_zhipin")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)
            
        cmd = [
            chrome_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--start-maximized",
            "--disable-search-engine-choice-screen"
        ]
        
        print(f"正在启动Chrome...")
        self.chrome_process = subprocess.Popen(cmd, shell=True)
        time.sleep(4)
        print("Chrome启动完成，请在打开的浏览器中继续操作")
        
    def _connect_to_chrome(self):
        """连接到已启动的Chrome"""
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.debug_port}")
        
        print("正在连接到Chrome...")
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.wait = WebDriverWait(self.driver, 20)
            print("连接成功！")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
        
    def _fix_data_url(self):
        """修复data: URL问题"""
        try:
            current_url = self.driver.current_url
            if "data:" in current_url or current_url == "about:blank":
                print("检测到无效页面，尝试修复...")
                # 尝试刷新
                self.driver.refresh()
                time.sleep(2)
                return True
        except:
            pass
        return False
        
    def start_and_connect(self):
        """启动并连接"""
        try:
            self._start_chrome_with_debug()
            if self._connect_to_chrome():
                self._fix_data_url()
                return True
            return False
        except Exception as e:
            print(f"启动Chrome失败: {e}")
            return False
            
    def connect_only(self):
        """仅连接到已有的Chrome调试实例"""
        return self._connect_to_chrome()
            
    def open_website(self):
        """打开网站"""
        print("\n正在打开Boss直聘网站...")
        
        try:
            # 确保在第一个标签页操作
            if self.driver.window_handles:
                self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            pass
            
        self.driver.get("https://www.zhipin.com/")
        time.sleep(3)
        
        # 检查是否成功
        current_url = self.driver.current_url
        title = self.driver.title
        print(f"当前URL: {current_url}")
        print(f"页面标题: {title}")
        
        success = "zhipin" in current_url or "BOSS直聘" in title
        if success:
            print("✓ Boss直聘网站已打开")
        else:
            print("✗ 网站打开可能有问题，请在浏览器中确认")
            
        return success
        
    def wait_for_login(self):
        """等待登录"""
        print("\n" + "="*50)
        print("【登录操作提示】")
        print("1. 请在浏览器中点击右上角'登录'按钮")
        print("2. 使用手机APP扫码完成登录")
        print("3. 登录成功后，回到本窗口按回车键继续")
        print("="*50)
        input("\n请完成登录后按回车键继续 >>> ")
        print("继续执行任务...")
        
    def search_jobs(self, keyword="开发者", city="苏州"):
        """搜索职位"""
        try:
            print(f"\n开始搜索: 城市={city}, 关键词={keyword}")
            
            # 切换城市
            self._switch_city(city)
            
            # 输入搜索关键词
            try:
                search_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input"))
                )
                search_input.clear()
                search_input.send_keys(keyword)
                time.sleep(1)
            except:
                print("未找到搜索框，尝试备用选择器")
                search_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder]"))
                )
                search_input.clear()
                search_input.send_keys(keyword)
                time.sleep(1)
            
            # 点击搜索按钮
            try:
                search_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-btn"))
                )
                search_btn.click()
            except:
                print("尝试按回车键搜索")
                search_input.send_keys("\n")
                
            time.sleep(3)
            print("搜索请求已发送")
            
        except Exception as e:
            print(f"搜索过程出错: {e}")
            
    def _switch_city(self, target_city):
        """切换城市"""
        try:
            city_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.city-select, span.city-name"))
            )
            current_city = city_btn.text.strip()
            print(f"当前城市: {current_city}")
            
            if current_city == target_city:
                print(f"城市已是 {target_city}")
                return
                
            city_btn.click()
            time.sleep(1)
            
            # 选择城市
            city_links = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a, .city-box a")
            for link in city_links:
                if link.text.strip() == target_city:
                    link.click()
                    print(f"已切换到: {target_city}")
                    time.sleep(2)
                    return
                    
            print(f"未找到城市选择列表，请手动切换到 {target_city}")
            
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def set_filters(self):
        """设置筛选条件"""
        try:
            print("\n正在设置筛选条件...")
            
            # 全职
            try:
                fulltime = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='全职']/parent::a"))
                )
                fulltime.click()
                print("已筛选: 全职")
            except:
                print("全职筛选设置失败，继续...")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"设置筛选条件出错: {e}")
            
    def collect_jobs(self, max_count=10):
        """收集职位信息"""
        print(f"\n正在收集职位信息（最多{max_count}条）...")
        
        try:
            # 等待职位列表加载
            job_cards = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box"))
            )
            
            if not job_cards:
                print("未找到职位列表")
                return
                
            print(f"当前页面找到 {len(job_cards)} 个职位")
            
            collected = 0
            for i, card in enumerate(job_cards):
                if collected >= max_count:
                    break
                    
                try:
                    title = card.find_element(By.CSS_SELECTOR, "div.job-title a").text.strip()
                    salary = card.find_element(By.CSS_SELECTOR, "div.job-title span").text.strip()
                    company = card.find_element(By.CSS_SELECTOR, "div.company-info a").text.strip()
                    
                    # 地点
                    location_elems = card.find_elements(By.CSS_SELECTOR, "div.job-tag span")
                    location = location_elems[0].text.strip() if location_elems else "未知"
                    
                    print(f"{collected+1}. {title} - {company} - {salary} - {location}")
                    
                    # 简单薪资检查
                    if "10-" in salary or "11-" in salary or "12-" in salary or "13-" in salary:
                        self.jobs_data.append({
                            "职位名称": title,
                            "公司名称": company,
                            "薪资范围": salary,
                            "工作地点": location,
                            "备注": "薪资在10k-13k范围内或接近"
                        })
                        collected += 1
                    
                except Exception as e:
                    print(f"处理第{i+1}个职位出错: {e}")
                    continue
                    
            print(f"\n收集完成，共收集 {len(self.jobs_data)} 条符合条件的记录")
            
        except Exception as e:
            print(f"收集职位出错: {e}")
            
    def export_excel(self, filename="苏州_开发者_职位汇总.xlsx"):
        """导出Excel"""
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            df.to_excel(filename, index=False, engine="openpyxl")
            full_path = os.path.abspath(filename)
            print(f"\n{'='*50}")
            print(f"✓ 数据导出成功！")
            print(f"文件位置: {full_path}")
            print(f"记录数量: {len(self.jobs_data)} 条")
            print(f"{'='*50}")
        else:
            print("\n没有找到符合条件的职位数据")
            
    def run(self):
        """主流程"""
        print("\n" + "="*60)
        print("Boss直聘职位搜索工具")
        print("="*60)
        print("\n请选择连接方式:")
        print("1. 自动启动Chrome浏览器并连接")
        print("2. 手动连接到已打开的Chrome调试模式")
        print("3. 退出程序")
        
        while True:
            choice = input("\n请输入选项 (1/2/3): ").strip()
            if choice == "1":
                if not self.start_and_connect():
                    print("启动失败，请重试或选择手动连接")
                    continue
                break
            elif choice == "2":
                print("\n手动连接说明:")
                print("1. 关闭所有Chrome浏览器")
                print('2. 按Win+R，输入: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222')
                print("3. 按回车启动Chrome")
                print("4. 完成后按回车继续")
                input("\n准备好后按回车键开始连接...")
                if not self.connect_only():
                    print("连接失败，请确认Chrome已正确启动")
                    continue
                break
            elif choice == "3":
                print("退出程序")
                return
            else:
                print("无效选项，请重新输入")
        
        # 打开网站
        self.open_website()
        
        # 等待登录
        self.wait_for_login()
        
        # 搜索职位
        self.search_jobs()
        
        # 设置筛选
        self.set_filters()
        
        # 收集职位
        self.collect_jobs()
        
        # 导出Excel
        self.export_excel()
        
        print("\n任务完成！")
        input("\n按回车键退出程序...")
        
    def close(self):
        """关闭资源"""
        if self.driver:
            try:
                # 不要关闭浏览器，让用户自己保留
                print("\n程序结束，浏览器窗口保持打开状态")
            except:
                pass

if __name__ == "__main__":
    app = BossZhipinAutomation()
    try:
        app.run()
    finally:
        app.close()
