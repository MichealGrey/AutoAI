import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class BossZhipinAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.jobs_data = []
        self.main_window_handle = None  # 保存主窗口句柄
        
    def init_driver(self):
        """初始化Chrome浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-notifications")
        # 禁用新标签页打开，改为在当前标签页打开链接
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def open_website(self):
        """打开Boss直聘网站"""
        self.driver.get("https://www.zhipin.com/")
        time.sleep(3)
        print("Boss直聘网站已打开")
        # 保存主窗口句柄
        self.main_window_handle = self.driver.current_window_handle
        print(f"主窗口句柄已保存")
        
    def wait_for_login(self):
        """等待用户登录"""
        print("\n" + "="*50)
        print("请在浏览器中完成以下操作：")
        print("1. 点击页面右上角的'登录'按钮")
        print("2. 使用扫码或账号密码方式登录")
        print("3. 登录成功后，请点击回车继续")
        print("="*50)
        
        # 等待用户输入确认登录
        input("请在登录完成后按回车键继续...")
        
        # 检查是否在主窗口
        try:
            if self.driver.current_window_handle != self.main_window_handle:
                print("检测到窗口变化，切回主窗口")
                self.driver.switch_to.window(self.main_window_handle)
        except:
            pass
        
        print("✓ 继续执行任务")
        time.sleep(2)
        
    def safe_click(self, element):
        """安全点击元素"""
        try:
            element.click()
        except:
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except:
                print("点击失败")
                
    def search_jobs(self, keyword="开发者", city="苏州"):
        """搜索职位"""
        try:
            print(f"\n开始搜索: 城市={city}, 关键词={keyword}")
            
            # 确保在主窗口操作
            self._ensure_main_window()
            
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
            self.safe_click(search_btn)
            time.sleep(3)
            
            print("搜索请求已发送，正在加载结果...")
            
        except Exception as e:
            print(f"搜索过程出错: {e}")
            self.driver.save_screenshot("search_error.png")
            
    def _ensure_main_window(self):
        """确保在主窗口"""
        try:
            if self.driver.switch_to.window(self.main_window_handle)
        except:
            pass
        # 关闭多余的标签页
        self._close_extra_tabs()
        
    def _close_extra_tabs(self):
        """关闭多余的标签页"""
        try:
            current_handle = self.driver.current_window_handle
            for handle in self.driver.window_handles:
                if handle != self.main_window_handle:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                    except:
                        pass
            self.driver.switch_to.window(self.main_window_handle)
        except:
            pass
            
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
                
            self.safe_click(city_btn)
            time.sleep(1)
            
            # 在城市列表中查找并点击目标城市
            city_links = self.driver.find_elements(By.CSS_SELECTOR, "div.city-list a, .city-list li, [class*='city'] a")
            )
            for link in city_links:
                if link.text.strip() == target_city:
                    self.safe_click(link)
                    print(f"已切换到城市: {target_city}")
                    time.sleep(2)
                    return
                    
            print(f"未找到城市 {target_city}")
            
        except Exception as e:
            print(f"切换城市出错: {e}")
            
    def set_filters(self):
        """设置筛选条件：薪资10k-13k，公司规模100-10000人以上，全职"""
        try:
            print("\n设置筛选条件...")
            
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
            self.driver.save_screenshot("filter_error.png")
            
    def _set_salary_filter(self):
        """设置薪资筛选"""
        try:
            # 点击薪资筛选下拉
            salary_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'filter-select') and contains(., '薪资')] | //span[text()='薪资']"))
            )
            self.safe_click(salary_dropdown)
            time.sleep(1)
            
            # 查找薪资选项 - Boss直聘的薪资选项通常是类似"10-15K"这样的
            salary_options = self.driver.find_elements(
                By.XPATH, "//ul[contains(@class, 'dropdown-list')]/li | //div[contains(@class, 'options')]//li")
            )
            
            # 点击包含10-15K的选项（覆盖10k-13k范围）
            for option in salary_options:
                option_text = option.text.strip()
                if "10-" in option_text or "10K" in option_text or "12-" in option_text:
                    self.safe_click(option)
                    print(f"选择薪资范围: {option_text}")
                    break
                    
        except Exception as e:
            print(f"设置薪资筛选出错: {e}")
            
    def _set_company_size_filter(self):
        """设置公司规模筛选"""
        try:
            # 点击公司规模筛选下拉
            size_dropdown = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'filter-select') and contains(., '规模')] | //span[text()='规模']"))
            )
            self.safe_click(size_dropdown)
            time.sleep(1)
            
            # 选择公司规模：100-499人、500-999人、1000-9999人、10000人以上
            size_options = self.driver.find_elements(
                By.XPATH, "//ul[contains(@class, 'dropdown-list')]/li | //div[contains(@class, 'options')]//li")
            )
            
            for option in size_options:
                option_text = option.text.strip()
                if "100-" in option_text or "500-" in option_text or "1000-" in option_text or "10000" in option_text:
                    self.safe_click(option)
                    print(f"选择公司规模: {option_text}")
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"设置公司规模筛选出错: {e}")
            
    def _set_job_type_filter(self):
        """设置工作类型筛选（全职）"""
        try:
            # 查找并点击"全职"选项
            fulltime_buttons = self.driver.find_elements(
                By.XPATH, "//span[text()='全职']/parent::a | //li[text()='全职'] | //a[text()='全职']")
            )
            
            for btn in fulltime_buttons:
                try:
                    self.safe_click(btn)
                    print("已选择: 全职")
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"设置工作类型筛选出错: {e}")
            
    def collect_jobs(self, max_pages=2):
        """收集职位信息并收藏"""
        print(f"\n开始收集职位信息，最多收集 {max_pages} 页")
        
        for page in range(max_pages):
            try:
                print(f"\n正在处理第 {page + 1} 页...")
                
                # 确保在主窗口
                self._ensure_main_window()
                
                # 等待职位列表加载
                job_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box, div.job-card"))
                )
                
                if not job_cards:
                    print("未找到更多职位")
                    break
                    
                print(f"找到 {len(job_cards)} 个职位卡片")
                
                for i, card in enumerate(job_cards):
                    try:
                        self._process_job_card(card, i)
                    except Exception as e:
                        print(f"处理第 {i+1} 个职位失败: {e}")
                        self._ensure_main_window()
                        continue
                
                # 尝试翻页
                if page < max_pages - 1:
                    if not self._go_to_next_page():
                        print("无法翻到下一页，结束收集")
                        break
                        
            except Exception as e:
                print(f"处理第 {page + 1} 页出错: {e}")
                break
                
    def _process_job_card(self, card, index):
        """处理单个职位卡片"""
        try:
            # 提取基本信息
            job_title = card.find_element(By.CSS_SELECTOR, "div.job-title a, a.job-name").text.strip()
            salary = card.find_element(By.CSS_SELECTOR, "div.job-title span, span.salary").text.strip()
            company = card.find_element(By.CSS_SELECTOR, "div.company-info a, a.company-name").text.strip()
            
            # 提取工作地点
            location_elements = card.find_elements(By.CSS_SELECTOR, "div.job-tag span, span.job-area")
            )
            location = location_elements[0].text.strip() if location_elements else "未知"
            
            # 解析薪资
            salary_min, salary_max = self._parse_salary_range(salary)
            print(f"职位 {index + 1}: {job_title} - {company} - {salary} (地点: {location})")
            
            # 检查薪资是否在10k-13k范围内
            if not (10000 <= salary_min <= 13000 or 10000 <= salary_max <= 13000 or 
                    (salary_min <= 10000 and salary_max >= 13000)):
                print(f"  → 薪资不在目标范围，跳过")
                return
            
            print(f"  → 薪资符合条件，准备查看详情")
            
            # 获取链接URL，直接在新标签页打开
            job_link_elem = card.find_element(By.CSS_SELECTOR, "div.job-title a, a.job-name")
            job_url = job_link_elem.get_attribute('href')
            print(f"  → 职位链接: {job_url}")
            
            # 修改策略：使用execute_script打开新标签
            self.driver.execute_script(f"window.open('{job_url}', '_blank');")
            time.sleep(2)
            
            # 切换到新标签页
            detail_window = None
            for handle in self.driver.window_handles:
                if handle != self.main_window_handle:
                    detail_window = handle
                    break
                    
            if detail_window:
                print(f"  → 打开新标签页，准备切换")
                self.driver.switch_to.window(detail_window)
                time.sleep(3)
                
                # 获取职位描述
                job_desc = self._get_job_description()
                
                # 点击收藏
                self._collect_job(job_title, company)
                
                # 保存数据
                self.jobs_data.append({
                    "职位名称": job_title,
                    "公司名称": company,
                    "薪资范围": salary,
                    "工作地点": location,
                    "职位描述": job_desc[:1000]  # 限制描述长度
                })
                
                # 关闭详情页
                print(f"  → 关闭详情页，返回主窗口")
                self.driver.close()
                self.driver.switch_to.window(self.main_window_handle)
                time.sleep(1)
                
        except Exception as e:
            print(f"处理职位失败: {e}")
            # 确保回到主页面
            try:
                self.driver.close()
            except:
                pass
            try:
                self.driver.switch_to.window(self.main_window_handle)
            except:
                pass
                
    def _parse_salary_range(self, salary_str):
        """解析薪资范围，返回(最小值, 最大值)"""
        try:
            # 处理如 "10-15K"、"12K-18K" 等格式
            salary_str = salary_str.upper().replace("K", "000")
            
            if "-" in salary_str:
                min_str, max_str = salary_str.split("-", 1)
                # 提取数字部分
                min_salary = int(''.join(filter(str.isdigit, min_str)))
                max_salary = int(''.join(filter(str.isdigit, max_str.split()[0])))
                return (min_salary, max_salary)
            else:
                # 单一薪资值
                salary = int(''.join(filter(str.isdigit, salary_str)))
                return (salary, salary)
        except:
            return (0, 0)
            
    def _get_job_description(self):
        """获取职位描述"""
        try:
            # 尝试多种选择器获取职位描述
            desc_selectors = [
                "div.job-sec-text",
                "div.job-detail-section div.text",
                "div[class*='desc'] div[class*='text']"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
                        timeout=3
                    )
                    return desc_element.text.strip()
                except:
                    continue
                    
            return "无法获取职位描述"
        except Exception as e:
            return f"获取描述失败: {str(e)}"
            
    def _collect_job(self, job_title, company):
        """点击收藏按钮"""
        try:
            # 尝试多种收藏按钮选择器
            collect_selectors = [
                "//button[contains(text(), '收藏')]",
                "//a[contains(text(), '收藏')]",
                "//div[contains(@class, 'collect')]/button",
                "//span[contains(text(), '收藏')]/parent::*",
                "//button[contains(@class, 'collect')]"
            ]
            
            for xpath in collect_selectors:
                try:
                    collect_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath)),
                        timeout=2
                    )
                    # 检查是否已收藏
                    btn_text = collect_btn.text.strip()
                    if "已收藏" in btn_text or "已收藏" in collect_btn.get_attribute("class"):
                        print(f"  → 该职位已收藏")
                        return
                        
                    collect_btn.click()
                    print(f"  ✓ 成功收藏: {job_title} - {company}")
                    time.sleep(1)
                    return
                except:
                    continue
                    
            print(f"  → 未找到收藏按钮")
            
        except Exception as e:
            print(f"  → 收藏失败: {e}")
            
    def _go_to_next_page(self):
        """跳转到下一页"""
        try:
            # 确保在主窗口
            self._ensure_main_window()
            
            # 查找下一页按钮
            next_selectors = [
                "//a[contains(text(), '下一页')]",
                "//div[contains(@class, 'page')]//a[last()]",
                "//a[contains(@class, 'next')]"
            ]
            
            for xpath in next_selectors:
                try:
                    next_btn = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath)),
                        timeout=3
                    )
                    
                    # 检查是否是最后一页
                    if "disabled" in next_btn.get_attribute("class") or next_btn.text.strip() != "下一页":
                        return False
                        
                    next_btn.click()
                    time.sleep(3)
                    return True
                except:
                    continue
                    
            return False
        except Exception as e:
            print(f"翻页失败: {e}")
            return False
            
    def export_to_excel(self, filename="苏州_开发者_职位汇总.xlsx"):
        """导出数据到Excel"""
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            # 调整列顺序
            df = df[["职位名称", "公司名称", "薪资范围", "工作地点", "职位描述"]]
            df.to_excel(filename, index=False, engine="openpyxl")
            print(f"\n{'='*50}")
            print(f"数据导出成功！")
            print(f"文件位置: {filename}")
            print(f"共收集 {len(self.jobs_data)} 条符合条件的职位信息")
            print(f"{'='*50}")
        else:
            print("\n未找到符合条件的职位数据")
            
    def run(self, keyword="开发者", city="苏州", max_pages=2):
        """运行自动化流程"""
        try:
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
                # 关闭所有标签页
                for handle in self.driver.window_handles:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                    except:
                        pass
            except:
                pass
            finally:
                self.driver.quit()
                print("\n浏览器已关闭")

if __name__ == "__main__":
    # 配置参数
    SEARCH_KEYWORD = "开发者"
    TARGET_CITY = "苏州"
    MAX_PAGES = 2  # 最多收集页数
    
    automation = BossZhipinAutomation()
    automation.run(
        keyword=SEARCH_KEYWORD,
        city=TARGET_CITY,
        max_pages=MAX_PAGES
    )
