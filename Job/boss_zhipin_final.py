import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class BossZhipinAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.jobs_data = []
        self.main_window = None  # 主窗口句柄
        
    def init_driver(self):
        """初始化Chrome浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-notifications")
        # 关键修复：防止打开新标签页时的问题
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-popup-blocking")
        # 禁止自动打开新窗口
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.popups": 1,
            "profile.default_content_setting_values.notifications": 2
        })
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def open_website(self):
        """打开Boss直聘网站"""
        print("正在打开Boss直聘网站...")
        self.driver.get("https://www.zhipin.com/")
        time.sleep(3)
        
        # 保存主窗口句柄
        self.main_window = self.driver.current_window_handle
        print(f"主窗口已保存: {self.main_window[:10]}...")
        print(f"当前页面: {self.driver.current_url}")
        print("Boss直聘网站已打开")
        
    def _switch_to_valid_window(self):
        """切换到有效的Boss直聘窗口"""
        try:
            # 检查所有窗口，找到有效的Boss直聘窗口
            for handle in self.driver.window_handles:
                try:
                    self.driver.switch_to.window(handle)
                    if "zhipin.com" in self.driver.current_url or "data:" not in self.driver.current_url:
                        if self.driver.current_url != "about:blank":
                            print(f"切换到窗口: {handle[:10]}..., URL: {self.driver.current_url[:30]}...")
                            self.main_window = handle
                            return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"切换窗口出错: {e}")
            return False
            
    def _close_blank_and_extra_windows(self):
        """关闭空白页和多余窗口"""
        try:
            valid_handles = []
            for handle in self.driver.window_handles:
                try:
                    self.driver.switch_to.window(handle)
                    url = self.driver.current_url
                    title = self.driver.title
                    if url != "about:blank" and "data:" not in url and len(url) > 10:
                        valid_handles.append((handle, url, title))
                    else:
                        print(f"关闭无效窗口: {handle[:10]}..., URL: {url}")
                        self.driver.close()
                except:
                    try:
                        self.driver.close()
                    except:
                        pass
                        
            # 切回第一个有效窗口
            if valid_handles:
                self.driver.switch_to.window(valid_handles[0][0])
                self.main_window = valid_handles[0][0]
                print(f"保留有效窗口: {valid_handles[0][0][:10]}..., URL: {valid_handles[0][1][:30]}...")
            else:
                print("没有找到有效窗口")
                
        except Exception as e:
            print(f"清理窗口出错: {e}")
            
    def wait_for_login(self):
        """等待用户登录"""
        print("\n" + "="*50)
        print("登录操作说明:")
        print("1. 请在浏览器中点击右上角'登录'按钮")
        print("2. 使用扫码或账号密码方式登录")
        print("3. 登录成功后，页面会显示你的用户名或头像")
        print("4. 重要：如果登录时打开了新标签页，请在登录后关闭它")
        print("="*50)
        
        # 先清理一次窗口
        self._close_blank_and_extra_windows()
        
        while True:
            try:
                # 确保在有效窗口
                self._switch_to_valid_window()
                
                # 检查是否已登录（查找用户名或用户头像）
                login_indicators = [
                    "a.name",
                    "div.user-info",
                    "a[href*='user']",
                    "a[href*='resume']",
                    "div.user-avatar",
                    ".user-area .name"
                ]
                
                for selector in login_indicators:
                    try:
                        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if elem and elem.is_displayed():
                            text = elem.text.strip() if elem.text else ""
                            if text and len(text) > 0:
                                print(f"\n✓ 检测到已登录！用户名: {text}")
                                print(f"  当前页面: {self.driver.current_url}")
                                time.sleep(1)
                                return
                    except:
                        continue
                        
            except Exception as e:
                print(f"检查登录状态出错: {e}")
                self._close_blank_and_extra_windows()
            
            time.sleep(2)
            print(".", end="", flush=True)
            
    def search_jobs(self, keyword="开发者", city="苏州"):
        """搜索职位"""
        try:
            print(f"\n开始搜索: 城市={city}, 关键词={keyword}")
            
            # 确保窗口有效
            self._close_blank_and_extra_windows()
            self._switch_to_valid_window()
            
            # 先切换城市到苏州
            self._switch_city(city)
            
            # 输入搜索关键词
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input, input[placeholder*='搜索']"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(1)
            
            # 点击搜索按钮
            search_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-btn, button[type='submit']"))
            )
            search_btn.click()
            time.sleep(3)
            
            # 清理可能打开的新窗口
            self._close_blank_and_extra_windows()
            
            print("搜索完成，当前页面:", self.driver.current_url)
            
        except Exception as e:
            print(f"搜索过程出错: {e}")
            self.driver.save_screenshot("search_error.png")
            self._close_blank_and_extra_windows()
            
    def _switch_city(self, target_city):
        """切换城市"""
        try:
            # 点击城市选择按钮
            city_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.city-select, span.city-name, a[href*='city']"))
            )
            current_city = city_btn.text.strip()
            print(f"当前城市: {current_city}")
            
            if current_city == target_city:
                print(f"城市已是 {target_city}，无需切换")
                return
                
            city_btn.click()
            time.sleep(1)
            
            # 在城市列表中查找并点击目标城市
            city_links = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a, .city-list li, [class*='city'] a")
            )
            for link in city_links:
                if link.text.strip() == target_city:
                    link.click()
                    print(f"已切换到城市: {target_city}")
                    time.sleep(2)
                    return
                    
            print(f"未找到城市 {target_city}")
            
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def set_filters(self):
        """设置筛选条件"""
        try:
            print("\n设置筛选条件...")
            
            # 确保在有效窗口
            self._close_blank_and_extra_windows()
            
            # 设置薪资范围
            self._set_salary_filter()
            
            # 设置公司规模
            self._set_company_size_filter()
            
            # 设置工作类型（全职）
            self._set_job_type_filter()
            
            print("筛选条件设置完成")
            time.sleep(2)
            
        except Exception as e:
            print(f"设置筛选条件出错: {e}")
            
    def _set_salary_filter(self):
        """设置薪资筛选"""
        try:
            salary_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'filter-select') and contains(., '薪资')] | //span[text()='薪资']"))
            )
            salary_dropdown.click()
            time.sleep(1)
            
            salary_options = self.driver.find_elements(
                By.XPATH, "//ul[contains(@class, 'dropdown-list')]/li | //div[contains(@class, 'options')]//li")
            )
            
            for option in salary_options:
                option_text = option.text.strip()
                if "10-" in option_text or "10K" in option_text or "12-" in option_text:
                    option.click()
                    print(f"选择薪资范围: {option_text}")
                    break
                    
        except Exception as e:
            print(f"设置薪资筛选出错: {e}")
            
    def _set_company_size_filter(self):
        """设置公司规模筛选"""
        try:
            size_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'filter-select') and contains(., '规模')] | //span[text()='规模']"))
            )
            size_dropdown.click()
            time.sleep(1)
            
            size_options = self.driver.find_elements(
                By.XPATH, "//ul[contains(@class, 'dropdown-list')]/li | //div[contains(@class, 'options')]//li")
            )
            
            for option in size_options:
                option_text = option.text.strip()
                if "100-" in option_text or "500-" in option_text or "1000-" in option_text or "10000" in option_text:
                    option.click()
                    print(f"选择公司规模: {option_text}")
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"设置公司规模筛选出错: {e}")
            
    def _set_job_type_filter(self):
        """设置工作类型筛选（全职）"""
        try:
            fulltime_buttons = self.driver.find_elements(
                By.XPATH, "//span[text()='全职']/parent::a | //li[text()='全职'] | //a[text()='全职']")
            )
            
            for btn in fulltime_buttons:
                try:
                    btn.click()
                    print("已选择: 全职")
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"设置全职筛选出错: {e}")
            
    def collect_jobs(self, max_pages=1):
        """收集职位信息（简化版本，不打开新标签页）"""
        print(f"\n开始收集职位信息，最多收集 {max_pages} 页")
        
        for page in range(max_pages):
            try:
                print(f"\n正在处理第 {page + 1} 页...")
                
                # 确保窗口有效
                self._close_blank_and_extra_windows()
                
                # 等待职位列表加载
                job_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box, div.job-card"))
                )
                
                if not job_cards:
                    print("未找到更多职位")
                    break
                    
                print(f"找到 {len(job_cards)} 个职位卡片")
                
                for i, card in enumerate(job_cards[:5]):  # 限制数量测试
                    try:
                        # 仅收集信息，不打开详情页
                        job_title = card.find_element(By.CSS_SELECTOR, "div.job-title a, a.job-name").get_attribute("title") or card.find_element(By.CSS_SELECTOR, "div.job-title a, a.job-name").text.strip()
                        salary = card.find_element(By.CSS_SELECTOR, "div.job-title span, span.salary").text.strip()
                        company = card.find_element(By.CSS_SELECTOR, "div.company-info a, a.company-name").text.strip()
                        
                        location_elems = card.find_elements(By.CSS_SELECTOR, "div.job-tag span, span.job-area")
                        location = location_elems[0].text.strip() if location_elems else "未知"
                        
                        # 解析薪资
                        salary_min, salary_max = self._parse_salary(salary)
                        print(f"{i+1}. {job_title} - {company} - {salary}")
                        
                        # 检查薪资范围（10k-13k）
                        if 10000 <= salary_min <= 13000 or 10000 <= salary_max <= 13000:
                            print(f"   ✓ 薪资符合条件")
                            self.jobs_data.append({
                                "职位名称": job_title,
                                "公司名称": company,
                                "薪资范围": salary,
                                "工作地点": location,
                                "职位描述": "请登录Boss直聘查看详情"
                            })
                        else:
                            print(f"   ✗ 薪资不在范围内（10k-13k）")
                            
                    except Exception as e:
                        print(f"处理职位失败: {e}")
                        continue
                
            except Exception as e:
                print(f"处理第 {page + 1} 页出错: {e}")
                break
                
    def _parse_salary(self, salary_str):
        """解析薪资字符串"""
        try:
            salary_str = salary_str.upper().replace("K", "000")
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
            df = df[["职位名称", "公司名称", "薪资范围", "工作地点", "职位描述"]]
            df.to_excel(filename, index=False, engine="openpyxl")
            print(f"\n{'='*50}")
            print(f"数据导出成功！")
            print(f"文件位置: {filename}")
            print(f"共收集 {len(self.jobs_data)} 条符合条件的职位信息")
            print(f"{'='*50}")
        else:
            print("\n未找到符合条件的职位数据")
            
    def run(self, keyword="开发者", city="苏州", max_pages=1):
        """运行自动化流程"""
        try:
            print("="*50)
            print("Boss直聘职位搜索自动化工具")
            print("="*50)
            
            # 初始化
            self.init_driver()
            self.open_website()
            
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
            
            print("\n任务完成！")
            
        except Exception as e:
            print(f"\n任务执行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close()
            
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                print("正在关闭浏览器...")
                self.driver.quit()
                print("浏览器已关闭")
            except Exception as e:
                print(f"关闭浏览器出错: {e}")

if __name__ == "__main__":
    automation = BossZhipinAutomation()
    automation.run(
        keyword="开发者",
        city="苏州",
        max_pages=1  # 先测试1页
    )
