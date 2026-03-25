from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, SessionNotCreatedException, WebDriverException
from loguru import logger
import time
import os
import sys
import subprocess
import platform
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from JobSearch.config.jobConfig import JobSearchConfig, BOSS_URL, SALARY_OPTIONS, COMPANY_SIZE_OPTIONS, LOGIN_WAIT_TIMEOUT, PAGE_LOAD_TIMEOUT, SCROLL_PAUSE_TIME
import pandas as pd
from datetime import datetime
import random

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logger.warning("webdriver-manager未安装，将使用系统默认驱动")

class BossZhipinController:
    def __init__(self, config: JobSearchConfig = None, headless: bool = False):
        self.config = config or JobSearchConfig()
        self.driver = None
        self.headless = headless
        self.collected_jobs = []
        self.wait = None
    
    def _get_chrome_version(self):
        """获取Chrome浏览器版本"""
        chrome_version = None
        system = platform.system()
        
        try:
            if system == "Windows":
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                    chrome_version, _ = winreg.QueryValueEx(key, "version")
                except:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
                        chrome_version, _ = winreg.QueryValueEx(key, "version")
                    except:
                        try:
                            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
                            chrome_version, _ = winreg.QueryValueEx(key, "version")
                        except:
                            pass
            elif system == "Darwin":
                result = subprocess.run(
                    ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    chrome_version = result.stdout.strip().split()[-1]
            elif system == "Linux":
                result = subprocess.run(["google-chrome", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    chrome_version = result.stdout.strip().split()[-1]
        except Exception as e:
            logger.warning(f"获取Chrome版本失败: {e}")
        
        return chrome_version
    
    def _check_chromedriver_exists(self):
        """检查ChromeDriver是否存在"""
        try:
            result = subprocess.run(
                ["chromedriver", "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"系统ChromeDriver版本: {version}")
                return True
        except FileNotFoundError:
            logger.warning("系统未找到ChromeDriver")
        except Exception as e:
            logger.warning(f"检查ChromeDriver失败: {e}")
        return False
    
    def _check_chrome_installed(self):
        """检查Chrome浏览器是否已安装"""
        chrome_version = self._get_chrome_version()
        if chrome_version:
            logger.info(f"检测到Chrome浏览器版本: {chrome_version}")
            return True
        else:
            logger.error("未检测到Chrome浏览器，请先安装Chrome")
            return False
    
    def _get_chrome_driver_path(self):
        """获取ChromeDriver路径，如果不存在则自动下载"""
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                logger.info("正在使用webdriver-manager自动下载/更新ChromeDriver...")
                driver_path = ChromeDriverManager().install()
                logger.info(f"ChromeDriver路径: {driver_path}")
                return driver_path
            except Exception as e:
                logger.error(f"webdriver-manager下载驱动失败: {e}")
                return None
        return None
    
    def init_driver(self):
        logger.info("初始化浏览器驱动...")
        
        if not self._check_chrome_installed():
            raise RuntimeError("Chrome浏览器未安装，请先安装Chrome浏览器")
        
        chromedriver_exists = self._check_chromedriver_exists()
        driver_path = None
        
        if not chromedriver_exists:
            logger.info("系统未安装ChromeDriver，尝试自动下载...")
            driver_path = self._get_chrome_driver_path()
            if not driver_path:
                raise RuntimeError(
                    "ChromeDriver未安装且自动下载失败。\n"
                    "请手动安装:\n"
                    "1. pip install webdriver-manager\n"
                    "2. 或从 https://chromedriver.chromium.org/downloads 下载对应版本"
                )
        
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            if driver_path:
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT)
            logger.info("浏览器驱动初始化完成")
            
        except SessionNotCreatedException as e:
            error_msg = str(e)
            if "This version of ChromeDriver only supports Chrome version" in error_msg:
                logger.error(f"ChromeDriver版本与Chrome浏览器版本不匹配: {error_msg}")
                if WEBDRIVER_MANAGER_AVAILABLE:
                    logger.info("尝试使用webdriver-manager下载匹配版本的驱动...")
                    try:
                        driver_path = ChromeDriverManager().install()
                        service = Service(executable_path=driver_path)
                        self.driver = webdriver.Chrome(service=service, options=options)
                        self.driver.maximize_window()
                        self.wait = WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT)
                        logger.info("浏览器驱动初始化完成")
                        return
                    except Exception as e2:
                        logger.error(f"自动下载匹配版本驱动失败: {e2}")
                raise RuntimeError(
                    f"ChromeDriver版本不匹配。\n"
                    f"Chrome版本: {self._get_chrome_version()}\n"
                    f"请运行: pip install webdriver-manager --upgrade"
                )
            raise
        except WebDriverException as e:
            logger.error(f"WebDriver异常: {e}")
            raise
        
    def open_website(self):
        logger.info(f"打开Boss直聘网站: {BOSS_URL}")
        self.driver.get(BOSS_URL)
        time.sleep(2)
        
    def wait_for_login(self):
        logger.info("等待用户扫码登录...")
        print("\n" + "="*50)
        print("请在浏览器中扫描二维码登录Boss直聘")
        print("登录成功后脚本将自动继续执行")
        print("="*50 + "\n")
        
        start_time = time.time()
        while time.time() - start_time < LOGIN_WAIT_TIMEOUT:
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".nav-figure")
                logger.info("登录成功！")
                return True
            except NoSuchElementException:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, ".user-nav")
                    logger.info("登录成功！")
                    return True
                except NoSuchElementException:
                    time.sleep(2)
                    continue
        
        logger.error("登录超时，请重新运行脚本")
        return False
    
    def search_jobs(self):
        logger.info(f"搜索职位: {self.config.keyword}")
        
        try:
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='搜索'], .search-input, input[name='query']"))
            )
            search_box.clear()
            search_box.send_keys(self.config.keyword)
            
            search_btn = self.driver.find_element(By.CSS_SELECTOR, ".search-btn, button[type='submit']")
            search_btn.click()
            time.sleep(3)
            
            self._apply_filters()
            return True
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return False
    
    def _apply_filters(self):
        logger.info("应用筛选条件...")
        
        try:
            self._select_city()
            self._select_salary()
            self._select_company_size()
            time.sleep(2)
        except Exception as e:
            logger.warning(f"筛选条件应用部分失败: {e}")
    
    def _select_city(self):
        try:
            city_selector = self.driver.find_element(By.CSS_SELECTOR, "[ka='search-job-city']")
            city_selector.click()
            time.sleep(1)
            
            city_items = self.driver.find_elements(By.CSS_SELECTOR, ".city-area a, .city-list a")
            for item in city_items:
                if self.config.city in item.text:
                    item.click()
                    logger.info(f"已选择城市: {self.config.city}")
                    time.sleep(1)
                    break
        except Exception as e:
            logger.warning(f"选择城市失败: {e}")
    
    def _select_salary(self):
        try:
            salary_selector = self.driver.find_element(By.CSS_SELECTOR, "[ka='search-salary']")
            salary_selector.click()
            time.sleep(1)
            
            target_salary = f"{self.config.salary_min}-{self.config.salary_max}K"
            salary_items = self.driver.find_elements(By.CSS_SELECTOR, ".salary-select a, .dropdown-menu a")
            
            for item in salary_items:
                if target_salary in item.text or f"{self.config.salary_min}-{self.config.salary_max}" in item.text:
                    item.click()
                    logger.info(f"已选择薪资: {target_salary}")
                    time.sleep(1)
                    break
        except Exception as e:
            logger.warning(f"选择薪资失败: {e}")
    
    def _select_company_size(self):
        try:
            size_selector = self.driver.find_element(By.CSS_SELECTOR, "[ka='search-scale']")
            size_selector.click()
            time.sleep(1)
            
            size_items = self.driver.find_elements(By.CSS_SELECTOR, ".scale-select a, .dropdown-menu a")
            target_sizes = []
            
            if self.config.company_size_min >= 100 and self.config.company_size_max >= 10000:
                target_sizes = ["100-499", "500-999", "1000-9999", "10000"]
            elif self.config.company_size_min >= 100:
                target_sizes = ["100-499", "500-999"]
            
            for item in size_items:
                for target in target_sizes:
                    if target in item.text:
                        item.click()
                        logger.info(f"已选择公司规模: {item.text}")
                        time.sleep(0.5)
                        break
        except Exception as e:
            logger.warning(f"选择公司规模失败: {e}")
    
    def collect_and_favorite_jobs(self):
        logger.info("开始收集并收藏职位...")
        
        collected_count = 0
        page = 1
        
        while collected_count < self.config.max_jobs:
            logger.info(f"正在处理第 {page} 页...")
            
            self._scroll_page()
            
            job_items = self.driver.find_elements(By.CSS_SELECTOR, ".job-list li, .search-job-result li, [ka='search-job-item']")
            
            if not job_items:
                job_items = self.driver.find_elements(By.CSS_SELECTOR, "li[data-jid]")
            
            for job_item in job_items:
                if collected_count >= self.config.max_jobs:
                    break
                
                try:
                    job_info = self._extract_job_info(job_item)
                    
                    if job_info and self._is_job_matching(job_info):
                        favorite_btn = job_item.find_element(By.CSS_SELECTOR, ".favorite-btn, [ka='search-job-favor'], .collect")
                        
                        if "active" not in favorite_btn.get_attribute("class"):
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", favorite_btn)
                            time.sleep(0.5)
                            
                            try:
                                favorite_btn.click()
                            except ElementClickInterceptedException:
                                self.driver.execute_script("arguments[0].click();", favorite_btn)
                            
                            logger.info(f"已收藏: {job_info['title']} - {job_info['company']}")
                            time.sleep(random.uniform(1, 2))
                        
                        self.collected_jobs.append(job_info)
                        collected_count += 1
                        
                except Exception as e:
                    logger.debug(f"处理职位时出错: {e}")
                    continue
            
            if not self._go_to_next_page():
                logger.info("没有更多页面了")
                break
            
            page += 1
            time.sleep(2)
        
        logger.info(f"共收集 {len(self.collected_jobs)} 个职位")
        return self.collected_jobs
    
    def _scroll_page(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for _ in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    def _extract_job_info(self, job_item):
        try:
            title = job_item.find_element(By.CSS_SELECTOR, ".job-title, .job-name, [ka='search-job-name']").text
            
            try:
                company = job_item.find_element(By.CSS_SELECTOR, ".company-name, .name, [ka='search-job-company']").text
            except:
                company = "未知公司"
            
            try:
                salary = job_item.find_element(By.CSS_SELECTOR, ".salary, .red, [ka='search-job-salary']").text
            except:
                salary = "薪资面议"
            
            try:
                location = job_item.find_element(By.CSS_SELECTOR, ".job-area, .area").text
            except:
                location = self.config.city
            
            try:
                experience = job_item.find_element(By.CSS_SELECTOR, ".job-info span:first-child, .tag-list li:first-child").text
            except:
                experience = "不限"
            
            try:
                education = job_item.find_element(By.CSS_SELECTOR, ".job-info span:nth-child(2), .tag-list li:nth-child(2)").text
            except:
                education = "不限"
            
            try:
                company_size = job_item.find_element(By.CSS_SELECTOR, ".company-tag li:nth-child(2), .info-desc").text
            except:
                company_size = "未知规模"
            
            try:
                job_desc = job_item.find_element(By.CSS_SELECTOR, ".job-desc, .info-desc").text
            except:
                job_desc = ""
            
            try:
                job_url = job_item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            except:
                job_url = ""
            
            return {
                "title": title,
                "company": company,
                "salary": salary,
                "location": location,
                "experience": experience,
                "education": education,
                "company_size": company_size,
                "description": job_desc,
                "url": job_url,
                "collect_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.debug(f"提取职位信息失败: {e}")
            return None
    
    def _is_job_matching(self, job_info):
        if self.config.keyword.lower() not in job_info['title'].lower():
            if self.config.keyword.lower() not in job_info['description'].lower():
                return False
        return True
    
    def _go_to_next_page(self):
        try:
            next_btn = self.driver.find_element(By.CSS_SELECTOR, ".next, [ka='page-next'], .page-next")
            
            if "disabled" in next_btn.get_attribute("class"):
                return False
            
            next_btn.click()
            return True
            
        except NoSuchElementException:
            return False
    
    def export_to_excel(self, filename: str = None):
        if not self.collected_jobs:
            logger.warning("没有收集到职位数据")
            return None
        
        if filename is None:
            filename = f"jobs_{self.config.city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.config.output_path, filename)
        
        df = pd.DataFrame(self.collected_jobs)
        
        columns_order = ['title', 'company', 'salary', 'location', 'experience', 'education', 'company_size', 'description', 'url', 'collect_time']
        df = df[[col for col in columns_order if col in df.columns]]
        
        df.columns = ['职位名称', '公司名称', '薪资范围', '工作地点', '经验要求', '学历要求', '公司规模', '职位描述', '职位链接', '收藏时间']
        
        df.to_excel(filepath, index=False, engine='openpyxl')
        logger.info(f"数据已导出到: {filepath}")
        
        return filepath
    
    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")
    
    def run(self):
        try:
            self.init_driver()
            self.open_website()
            
            if not self.wait_for_login():
                return None, None
            
            if not self.search_jobs():
                return None, None
            
            self.collect_and_favorite_jobs()
            filepath = self.export_to_excel()
            
            return self.collected_jobs, filepath
            
        except Exception as e:
            logger.error(f"运行出错: {e}")
            return None, None
        finally:
            self.close()
