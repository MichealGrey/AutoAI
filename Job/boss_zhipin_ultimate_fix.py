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
        """初始化Chrome浏览器 - 终极修复版本"""
        options = webdriver.ChromeOptions()
        
        # 基础设置
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 关键修复：解决 data: 问题
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        # 禁用 sandbox 和 GPU，解决一些兼容性问题
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        # 添加用户数据目录（避免首次启动提示）
        user_data_dir = os.path.join(os.path.expanduser("~"), "chrome_boss_zhipin")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # 禁用提示栏
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        
        print("正在启动Chrome浏览器...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # 绕过检测
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome浏览器启动成功")
        
    def open_website(self):
        """打开Boss直聘网站 - 带重试机制"""
        print("正在打开Boss直聘网站...")
        
        # 修复：先访问一个空白页，再访问目标网站
        self.driver.get("about:blank")
        time.sleep(1)
        
        max_retries = 3
        for i in range(max_retries):
            try:
                self.driver.get("https://www.zhipin.com/")
                time.sleep(3)
                
                # 检查是否成功加载
                if "zhipin.com" in self.driver.current_url:
                    print(f"✓ Boss直聘网站已打开")
                    print(f"  当前URL: {self.driver.current_url}")
                    print(f"  页面标题: {self.driver.title}")
                    return True
                elif "data:" in self.driver.current_url or self.driver.current_url == "about:blank":
                    print(f"  第{i+1}次尝试: 页面未正确加载，重试...")
                    # 尝试刷新
                    self.driver.refresh()
                    time.sleep(2)
                    continue
                else:
                    print(f"  打开了其他页面: {self.driver.current_url}")
                    return True
            except Exception as e:
                print(f"  第{i+1}次尝试失败: {e}")
                time.sleep(2)
        
        print("✗ 无法打开Boss直聘网站")
        return False
        
    def _ensure_valid_page(self):
        """确保当前页面是有效的页面"""
        try:
            current_url = self.driver.current_url
            if "data:" in current_url or current_url == "about:blank":
                print("检测到无效页面，尝试重新加载...")
                self.driver.get("https://www.zhipin.com/")
                time.sleep(3)
                return True
        except:
            pass
        return False
        
    def wait_for_login(self):
        """等待用户登录"""
        print("\n" + "="*50)
        print("登录操作说明:")
        print("1. 请在浏览器中点击右上角'登录'按钮")
        print("2. 使用扫码或账号密码方式登录")
        print("3. 登录成功后，页面会显示你的用户名或头像")
        print("4. 然后按回车键继续")
        print("="*50)
        
        # 确保页面有效
        self._ensure_valid_page()
        
        # 等待用户输入，简单直接的方式
        input("\n请完成登录后，回到这里按回车键继续 >>> ")
        
        # 检查登录状态
        print("\n正在确认登录状态...")
        self._ensure_valid_page()
        print(f"当前页面: {self.driver.current_url}")
        print("✓ 继续执行任务")
        
    def search_jobs(self, keyword="开发者", city="苏州"):
        """搜索职位"""
        try:
            print(f"\n开始搜索: 城市={city}, 关键词={keyword}")
            
            self._ensure_valid_page()
            
            # 先切换城市
            self._switch_city(city)
            
            # 查找搜索输入框
            search_selectors = [
                "input.search-input",
                "input[placeholder*='搜索']",
                ".search-input-wrapper input"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
                    
            if not search_input:
                print("未找到搜索框")
                return
                
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(1)
            
            # 点击搜索按钮
            search_btn_selectors = [
                "button.search-btn",
                "button[type='submit']",
                ".search-btn-wrapper button"
            ]
            
            search_btn = None
            for selector in search_btn_selectors:
                try:
                    search_btn = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
                    
            if search_btn:
                search_btn.click()
                time.sleep(3)
                print("搜索完成")
                print(f"当前页面: {self.driver.current_url}")
            else:
                print("未找到搜索按钮，尝试按回车键搜索")
                search_input.send_keys("\n")
                time.sleep(3)
            
        except Exception as e:
            print(f"搜索过程出错: {e}")
            
    def _switch_city(self, target_city):
        """切换城市"""
        try:
            self._ensure_valid_page()
            
            city_selectors = [
                "a.city-select",
                "span.city-name",
                "a[href*='city']",
                ".city-box a"
            ]
            
            city_btn = None
            for selector in city_selectors:
                try:
                    city_btn = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
                    
            if not city_btn:
                print("未找到城市选择按钮")
                return
                
            current_city = city_btn.text.strip()
            print(f"当前城市: {current_city}")
            
            if current_city == target_city:
                print(f"城市已是 {target_city}，无需切换")
                return
                
            city_btn.click()
            time.sleep(1)
            
            # 查找城市列表
            city_links = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a, .city-popup a, .city-list li")
            )
            for link in city_links:
                try:
                    if link.text.strip() == target_city:
                        link.click()
                        print(f"已切换到城市: {target_city}")
                        time.sleep(2)
                        return
                except:
                    continue
                    
            print(f"未找到城市 {target_city}")
            
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def set_filters(self):
        """设置筛选条件"""
        try:
            print("\n设置筛选条件...")
            self._ensure_valid_page()
            
            # 设置薪资范围
            self._set_salary_filter()
            
            # 设置公司规模
            self._set_company_size_filter()
            
            # 设置工作类型（全职）
            self._set_fulltime_filter()
            
            print("筛选条件设置完成")
            time.sleep(2)
            
        except Exception as e:
            print(f"设置筛选条件出错: {e}")
            
    def _set_salary_filter(self):
        """设置薪资筛选"""
        try:
            salary_xpaths = [
                "//div[contains(@class, 'filter-select') and contains(., '薪资')]",
                "//span[text()='薪资']",
                "//div[contains(text(), '薪资')]"
            ]
            
            for xpath in salary_xpaths:
                try:
                    salary_dropdown = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    salary_dropdown.click()
                    time.sleep(1)
                    break
                except:
                    continue
            
            # 选择10-15K的选项
            salary_options = self.driver.find_elements(
                By.XPATH, "//ul/li[contains(text(), '10-') or contains(text(), '10K') or contains(text(), '12-')]"
            )
            for option in salary_options:
                try:
                    option.click()
                    print(f"选择薪资范围: {option.text.strip()}")
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"设置薪资筛选出错: {e}")
            
    def _set_company_size_filter(self):
        """设置公司规模筛选"""
        try:
            size_xpaths = [
                "//div[contains(@class, 'filter-select') and contains(., '规模')]",
                "//span[text()='规模']"
            ]
            
            for xpath in size_xpaths:
                try:
                    size_dropdown = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    size_dropdown.click()
                    time.sleep(1)
                    break
                except:
                    continue
            
            # 选择公司规模选项
            size_options = self.driver.find_elements(
                By.XPATH, "//ul/li[contains(text(), '100-') or contains(text(), '500-') or contains(text(), '1000-')]"
            )
            for option in size_options:
                try:
                    option.click()
                    print(f"选择公司规模: {option.text.strip()}")
                    time.sleep(0.3)
                except:
                    continue
                    
        except Exception as e:
            print(f"设置公司规模筛选出错: {e}")
            
    def _set_fulltime_filter(self):
        """设置全职筛选"""
        try:
            fulltime_xpaths = [
                "//span[text()='全职']/parent::a",
                "//a[text()='全职']",
                "//li[text()='全职']"
            ]
            
            for xpath in fulltime_xpaths:
                try:
                    fulltime_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    fulltime_btn.click()
                    print("已选择: 全职")
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"设置全职筛选出错: {e}")
            
    def collect_jobs(self, max_pages=1):
        """收集职位信息"""
        print(f"\n开始收集职位信息，最多收集 {max_pages} 页")
        
        for page in range(max_pages):
            try:
                print(f"\n正在处理第 {page + 1} 页...")
                self._ensure_valid_page()
                
                # 等待职位列表加载
                job_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box, div.job-card"))
                )
                
                if not job_cards:
                    print("未找到更多职位")
                    break
                    
                print(f"找到 {len(job_cards)} 个职位卡片")
                
                for i, card in enumerate(job_cards[:5]):  # 测试阶段限制数量
                    try:
                        self._process_single_job(card, i)
                    except Exception as e:
                        print(f"处理职位 {i+1} 失败: {e}")
                        continue
                
            except Exception as e:
                print(f"处理第 {page + 1} 页出错: {e}")
                break
                
    def _process_single_job(self, card, index):
        """处理单个职位卡片"""
        try:
            # 提取基本信息
            title_elem = card.find_element(By.CSS_SELECTOR, "div.job-title a, a.job-name")
            job_title = title_elem.get_attribute("title") or title_elem.text.strip()
            
            salary_elem = card.find_element(By.CSS_SELECTOR, "div.job-title span, span.salary")
            salary = salary_elem.text.strip()
            
            company_elem = card.find_element(By.CSS_SELECTOR, "div.company-info a, a.company-name")
            company = company_elem.text.strip()
            
            location_elems = card.find_elements(By.CSS_SELECTOR, "div.job-tag span, span.job-area")
            location = location_elems[0].text.strip() if location_elems else "未知"
            
            print(f"{index+1}. {job_title} - {company} - {salary} - {location}")
            
            # 解析薪资
            salary_min, salary_max = self._parse_salary(salary)
            
            # 检查薪资范围（10k-13k）
            if 10000 <= salary_min <= 13000 or 10000 <= salary_max <= 13000:
                print(f"   ✓ 薪资符合条件 (10k-13k)")
                
                # 获取职位链接
                job_url = title_elem.get_attribute('href')
                print(f"   职位链接: {job_url[:50]}..." if len(job_url) > 50 else job_url)
                
                # 保存数据
                self.jobs_data.append({
                    "职位名称": job_title,
                    "公司名称": company,
                    "薪资范围": salary,
                    "工作地点": location,
                    "职位链接": job_url,
                    "职位描述": "请点击链接查看详情"
                })
            else:
                print(f"   ✗ 薪资不在范围内 (期望:10k-13k，实际:{salary_min/1000:.0f}k-{salary_max/1000:.0f}k)")
                
        except Exception as e:
            print(f"处理职位失败: {e}")
            
    def _parse_salary(self, salary_str):
        """解析薪资字符串"""
        try:
            # 处理如 "10-15K"、"12K-18K"、"15K以上" 等格式
            salary_str = salary_str.upper().replace("K", "000").replace("以上", "")
            
            if "-" in salary_str:
                min_str, max_str = salary_str.split("-", 1)
                min_sal = int(''.join(filter(str.isdigit, min_str)))
                max_sal = int(''.join(filter(str.isdigit, max_str.split()[0])))
                return (min_sal, max_sal)
            else:
                sal = int(''.join(filter(str.isdigit, salary_str)))
                return (sal, sal)
        except:
            return (0, 0)
            
    def export_to_excel(self, filename="苏州_开发者_职位汇总.xlsx"):
        """导出数据到Excel"""
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            # 调整列顺序
            df = df[["职位名称", "公司名称", "薪资范围", "工作地点", "职位链接", "职位描述"]]
            df.to_excel(filename, index=False, engine="openpyxl")
            print(f"\n{'='*50}")
            print(f"数据导出成功！")
            print(f"文件位置: {os.path.abspath(filename)}")
            print(f"共收集 {len(self.jobs_data)} 条符合条件的职位信息")
            print(f"{'='*50}")
        else:
            print("\n未找到符合条件的职位数据")
            
    def run(self, keyword="开发者", city="苏州", max_pages=1):
        """运行自动化流程"""
        success = False
        try:
            print("="*50)
            print("Boss直聘职位搜索自动化工具")
            print("="*50)
            
            # 初始化
            self.init_driver()
            if not self.open_website():
                print("无法打开网站，退出")
                return
            
            # 等待登录
            self.wait_for_login()
            
            # 搜索职位
            self.search_jobs(keyword=keyword, city=city)
            
            # 设置筛选条件
            self.set_filters()
            
            # 收集职位信息
            self.collect_jobs(max_pages=max_pages)
            
            # 导出Excel
            self.export_to_excel()
            
            success = True
            print("\n✓ 任务完成！")
            
        except Exception as e:
            print(f"\n✗ 任务执行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close()
            return success
            
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                print("\n正在关闭浏览器...")
                self.driver.quit()
                print("浏览器已关闭")
            except Exception as e:
                print(f"关闭浏览器出错: {e}")

if __name__ == "__main__":
    print("\n欢迎使用Boss直聘职位搜索工具！")
    print("="*50)
    
    # 可配置参数
    SEARCH_KEYWORD = "开发者"
    TARGET_CITY = "苏州"
    MAX_PAGES = 1
    
    automation = BossZhipinAutomation()
    automation.run(
        keyword=SEARCH_KEYWORD,
        city=TARGET_CITY,
        max_pages=MAX_PAGES
    )
    
    input("\n按回车键退出程序...")
