import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BossZhipinAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.jobs_data = []
        
    def init_driver(self):
        """初始化Chrome浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
        
    def open_website(self):
        """打开Boss直聘网站"""
        self.driver.get("https://www.zhipin.com/")
        time.sleep(3)
        
    def search_jobs(self, keyword="开发者", city="苏州", min_salary=10000, max_salary=13000):
        """搜索职位"""
        try:
            # 输入搜索关键词
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='搜索']"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(1)
            
            # 选择城市
            city_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '北京') or contains(text(), '全国')]"))
            )
            city_btn.click()
            time.sleep(1)
            
            # 输入苏州
            city_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='城市']"))
            )
            city_input.clear()
            city_input.send_keys("苏州")
            time.sleep(1)
            
            # 选择第一个搜索结果（苏州）
            suzhou_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), '苏州')]"))
            )
            suzhou_option.click()
            time.sleep(1)
            
            # 点击搜索按钮
            search_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            search_btn.click()
            time.sleep(3)
            
            # 设置薪资范围
            self.set_salary_range(min_salary, max_salary)
            
            # 设置公司规模
            self.set_company_size()
            
            # 选择全职
            self.set_full_time()
            
        except Exception as e:
            print(f"搜索过程出错: {e}")
            self.driver.save_screenshot("search_error.png")
            
    def set_salary_range(self, min_salary, max_salary):
        """设置薪资范围"""
        try:
            # 点击薪资筛选
            salary_filter = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '薪资')]/following-sibling::div"))
            )
            salary_filter.click()
            time.sleep(1)
            
            # 查找自定义薪资输入
            # 这里可能需要根据实际页面结构调整
            print("请手动确认薪资筛选是否已设置为10k-13k")
            time.sleep(2)
            
        except Exception as e:
            print(f"设置薪资范围出错: {e}")
            
    def set_company_size(self):
        """设置公司规模 100-10000人以上"""
        try:
            # 点击公司规模筛选
            size_filter = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '规模')]/following-sibling::div"))
            )
            size_filter.click()
            time.sleep(1)
            
            # 选择100-499人和500-999人、1000-9999人、10000人以上
            size_options = self.driver.find_elements(
                By.XPATH, "//li[contains(text(), '100-499') or contains(text(), '500-999') or contains(text(), '1000-9999') or contains(text(), '10000')]"
            )
            for option in size_options:
                option.click()
                time.sleep(0.5)
            
        except Exception as e:
            print(f"设置公司规模出错: {e}")
            
    def set_full_time(self):
        """设置全职"""
        try:
            # 点击全职选项
            full_time_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '全职')]"))
            )
            full_time_btn.click()
            time.sleep(2)
            
        except Exception as e:
            print(f"设置全职出错: {e}")
            
    def collect_and_collect_jobs(self, max_pages=3):
        """收集职位信息并收藏"""
        page_count = 0
        
        while page_count < max_pages:
            try:
                # 等待职位列表加载
                job_cards = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job-card-box"))
                )
                
                for card in job_cards:
                    try:
                        # 提取职位信息
                        job_title = card.find_element(By.CSS_SELECTOR, "div.job-title a").text
                        salary = card.find_element(By.CSS_SELECTOR, "div.job-title span").text
                        company = card.find_element(By.CSS_SELECTOR, "div.company-info a").text
                        location = card.find_element(By.CSS_SELECTOR, "div.job-tag span").text
                        
                        # 检查薪资是否在范围内（10k-13k）
                        salary_num = self.parse_salary(salary)
                        if 10000 <= salary_num <= 13000:
                            # 点击进入职位详情
                            job_link = card.find_element(By.CSS_SELECTOR, "div.job-title a")
                            self.driver.execute_script("arguments[0].click();", job_link)
                            time.sleep(2)
                            
                            # 切换到新标签页
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            time.sleep(2)
                            
                            # 获取详细描述
                            try:
                                desc_element = self.wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-sec-text"))
                                )
                                job_desc = desc_element.text
                            except:
                                job_desc = "无法获取描述"
                            
                            # 点击收藏按钮
                            try:
                                collect_btn = self.wait.until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '收藏') or contains(@class, 'collect')]"))
                                )
                                collect_btn.click()
                                print(f"已收藏: {job_title} - {company}")
                                time.sleep(1)
                            except Exception as e:
                                print(f"收藏失败: {job_title} - {e}")
                            
                            # 保存数据
                            self.jobs_data.append({
                                "职位名称": job_title,
                                "公司名称": company,
                                "薪资": salary,
                                "工作地点": location,
                                "职位描述": job_desc[:500]  # 限制描述长度
                            })
                            
                            # 关闭详情页，返回列表页
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"处理职位卡片出错: {e}")
                        continue
                
                page_count += 1
                print(f"完成第 {page_count} 页")
                
                # 点击下一页
                if page_count < max_pages:
                    try:
                        next_btn = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '下一页')]"))
                        )
                        next_btn.click()
                        time.sleep(3)
                    except:
                        print("没有更多页面了")
                        break
                        
            except Exception as e:
                print(f"收集职位信息出错: {e}")
                break
                
    def parse_salary(self, salary_str):
        """解析薪资字符串为数字"""
        try:
            # 处理如 "10-15K" 这样的格式，取最小值
            if "K" in salary_str or "k" in salary_str:
                min_salary = salary_str.split("-")[0].replace("K", "").replace("k", "")
                return float(min_salary) * 1000
            return 0
        except:
            return 0
            
    def export_to_excel(self, filename="boss_jobs.xlsx"):
        """导出数据到Excel"""
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            df.to_excel(filename, index=False, engine="openpyxl")
            print(f"数据已导出到 {filename}，共 {len(self.jobs_data)} 条记录")
        else:
            print("没有找到符合条件的职位数据")
            
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")
            
    def run(self):
        """运行自动化流程"""
        try:
            print("开始Boss直聘自动化任务...")
            self.init_driver()
            self.open_website()
            
            print("请在浏览器中完成登录操作（扫码或账号密码）")
            print("登录完成后按回车键继续...")
            input("按回车继续...")
            
            self.search_jobs()
            self.collect_and_collect_jobs(max_pages=3)
            self.export_to_excel()
            
        except Exception as e:
            print(f"任务执行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close()

if __name__ == "__main__":
    automation = BossZhipinAutomation()
    automation.run()
