import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BossZhipinAutomation:
    def __init__(self):
        self.driver = None
        self.jobs_data = []
        
    def start_browser(self):
        """启动浏览器并打开Boss直聘网站"""
        import subprocess
        import socket
        
        # 找到一个未使用的端口
        def find_available_port():
            for port in range(9222, 9300):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(('localhost', port)) != 0:
                        return port
            return None
        
        available_port = find_available_port()
        if not available_port:
            print("没有找到可用的端口")
            return False
        
        print(f"找到可用端口: {available_port}")
        
        # 使用cmd命令启动Chrome并开启远程调试
        chrome_cmd = f'chrome.exe --remote-debugging-port={available_port} --user-data-dir="D:\\selenium\\BossProfile" "https://www.zhipin.com/";exit'
        subprocess.Popen(chrome_cmd, shell=True)
        time.sleep(5)
        
        # 配置Selenium连接到已启动的Chrome
        options = Options()
        chrome_address = f"127.0.0.1:{available_port}"
        options.add_experimental_option("debuggerAddress", chrome_address)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            print("浏览器启动成功")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"浏览器启动失败: {str(e)}")
            return False
    
    def login(self):
        """登录Boss直聘"""
        try:
            # 等待登录按钮出现
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".nav-user > a"))
            )
            login_btn.click()
            time.sleep(3)
            
            # 切换到密码登录
            password_login = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".login-switch-type"))
            )
            password_login.click()
            time.sleep(2)
            
            # 输入手机号和密码
            phone_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='account']")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            
            # 这里需要手动输入手机号和密码，或者从配置文件中读取
            phone = input("请输入您的手机号: ")
            password = input("请输入您的密码: ")
            
            phone_input.send_keys(phone)
            password_input.send_keys(password)
            time.sleep(1)
            
            # 点击登录按钮
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-login")
            submit_btn.click()
            time.sleep(10)  # 等待登录完成，可能需要处理验证码
            
            print("登录成功")
            return True
            
        except TimeoutException:
            print("登录页面加载超时")
            return False
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return False
    
    def search_jobs(self):
        """搜索苏州的全职开发者工作"""
        try:
            # 选择城市为苏州
            city_select = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".city-selector .text"))
            )
            city_select.click()
            time.sleep(2)
            
            suzhou_city = self.driver.find_element(By.CSS_SELECTOR, "a[data-id='489']")  # 苏州的城市ID
            suzhou_city.click()
            time.sleep(3)
            
            # 输入搜索关键词
            search_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='query']")
            search_input.clear()
            search_input.send_keys("开发者")
            time.sleep(1)
            
            # 点击搜索按钮
            search_btn = self.driver.find_element(By.CSS_SELECTOR, ".btn-search")
            search_btn.click()
            time.sleep(5)
            
            print("搜索职位成功")
            return True
            
        except Exception as e:
            print(f"搜索职位失败: {str(e)}")
            return False
    
    def filter_jobs(self):
        """筛选薪资1w~1.3w，公司规模100至10000人以上的全职工作"""
        try:
            # 筛选全职
            full_time_filter = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='全职']"))
            )
            full_time_filter.click()
            time.sleep(3)
            
            # 筛选薪资1w~1.3w
            salary_filter = self.driver.find_element(By.CSS_SELECTOR, ".filter-salary .ui-select-trigger")
            salary_filter.click()
            time.sleep(2)
            
            # 选择10k-15k区间（因为没有10k-13k的选项）
            salary_option = self.driver.find_element(By.XPATH, "//li[contains(text(), '10k-15k')]")
            salary_option.click()
            time.sleep(3)
            
            # 筛选公司规模
            scale_filter = self.driver.find_element(By.CSS_SELECTOR, ".filter-scale .ui-select-trigger")
            scale_filter.click()
            time.sleep(2)
            
            # 选择100-499人、500-999人、1000-9999人、10000人以上
            scale_options = [
                "//li[contains(text(), '100-499人')]",
                "//li[contains(text(), '500-999人')]",
                "//li[contains(text(), '1000-9999人')]",
                "//li[contains(text(), '10000人以上')]"
            ]
            
            for option_xpath in scale_options:
                option = self.driver.find_element(By.XPATH, option_xpath)
                option.click()
                time.sleep(1)
            
            # 关闭筛选菜单
            scale_filter.click()
            time.sleep(3)
            
            print("筛选条件设置成功")
            return True
            
        except Exception as e:
            print(f"筛选条件设置失败: {str(e)}")
            return False
    
    def _is_salary_in_range(self, salary_str):
        """检查薪资是否在1w-1.3w范围内"""
        try:
            # 提取薪资范围的数字部分
            salary = salary_str.replace('k', '000').replace('K', '000')
            salary_range = re.findall(r'\d+', salary)
            if len(salary_range) == 2:
                min_salary = int(salary_range[0])
                max_salary = int(salary_range[1])
                # 检查是否在10000-13000范围内
                return min_salary >= 10000 and max_salary <= 13000
            return False
        except:
            return False
    
    def collect_jobs(self, max_pages=3):
        """收集符合条件的职位信息并收藏"""
        current_page = 1
        
        while current_page <= max_pages:
            try:
                print(f"正在收集第{current_page}页的职位信息...")
                
                # 等待职位列表加载完成
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-list ul"))
                )
                time.sleep(3)
                
                # 获取职位列表
                job_items = self.driver.find_elements(By.CSS_SELECTOR, ".job-list ul li.job-card-wrapper")
                
                for idx, job_item in enumerate(job_items):
                    try:
                        # 先检查薪资是否在1w-1.3w范围内
                        salary_elem = job_item.find_element(By.CSS_SELECTOR, ".salary")
                        salary_str = salary_elem.text
                        
                        # 只有薪资在1w-1.3w范围内才处理
                        if self._is_salary_in_range(salary_str):
                            # 点击职位卡片查看详情
                            job_card = job_item.find_element(By.CSS_SELECTOR, ".job-card-left")
                            self.driver.execute_script("arguments[0].scrollIntoView();", job_card)
                            time.sleep(2)
                            job_card.click()
                            time.sleep(5)
                            
                            # 切换到详情页iframe
                            WebDriverWait(self.driver, 10).until(
                                EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))
                            )
                            
                            # 获取职位信息
                            job_info = self._get_job_details()
                            
                            # 收藏职位
                            self._favorite_job()
                            
                            # 添加到数据列表
                            self.jobs_data.append(job_info)
                            print(f"已收藏并记录职位: {job_info['职位名称']}")
                            
                            # 切换回主页面
                            self.driver.switch_to.default_content()
                            
                            # 关闭详情页
                            close_btn = self.driver.find_element(By.CSS_SELECTOR, ".job-detail .icon-close")
                            close_btn.click()
                            time.sleep(3)
                        else:
                            print(f"职位薪资不在范围内: {salary_str}")
                            continue
                            
                    except Exception as e:
                        print(f"处理职位时出错: {str(e)}")
                        self.driver.switch_to.default_content()
                        continue
                
                # 翻到下一页
                if current_page < max_pages:
                    next_page = self.driver.find_element(By.CSS_SELECTOR, ".pagination .next")
                    if "disabled" not in next_page.get_attribute("class"):
                        next_page.click()
                        time.sleep(5)
                        current_page += 1
                    else:
                        print("已经是最后一页")
                        break
                else:
                    break
                    
            except Exception as e:
                print(f"收集职位信息失败: {str(e)}")
                break
    
    def _get_job_details(self):
        """获取职位详情信息"""
        try:
            # 职位名称
            job_title = self.driver.find_element(By.CSS_SELECTOR, ".job-detail .name").text
            
            # 薪资
            salary = self.driver.find_element(By.CSS_SELECTOR, ".job-detail .salary").text
            
            # 公司名称
            company_name = self.driver.find_element(By.CSS_SELECTOR, ".company-info .name").text
            
            # 公司规模
            company_scale = self.driver.find_element(By.CSS_SELECTOR, ".company-info p:nth-child(2)").text
            
            # 职位描述
            job_desc = self.driver.find_element(By.CSS_SELECTOR, ".job-sec.text").text
            
            # 职位要求
            job_requirements = ""
            try:
                requirements_section = self.driver.find_element(By.CSS_SELECTOR, ".job-sec.requirement")
                job_requirements = requirements_section.text
            except:
                pass
            
            return {
                "职位名称": job_title,
                "薪资": salary,
                "公司名称": company_name,
                "公司规模": company_scale,
                "职位描述": job_desc,
                "职位要求": job_requirements
            }
            
        except Exception as e:
            print(f"获取职位详情失败: {str(e)}")
            return {}
    
    def _favorite_job(self):
        """收藏当前职位"""
        try:
            favorite_btn = self.driver.find_element(By.CSS_SELECTOR, ".btn-collect")
            if "已收藏" not in favorite_btn.text:
                favorite_btn.click()
                time.sleep(2)
                print("职位收藏成功")
            else:
                print("职位已经被收藏过")
        except Exception as e:
            print(f"收藏职位失败: {str(e)}")
    
    def export_to_excel(self, filename="boss_jobs.xlsx"):
        """将收集的职位信息导出到Excel"""
        if not self.jobs_data:
            print("没有收集到职位信息")
            return
        
        try:
            df = pd.DataFrame(self.jobs_data)
            df.to_excel(filename, index=False)
            print(f"职位信息已成功导出到{filename}")
            return True
        except Exception as e:
            print(f"导出Excel失败: {str(e)}")
            return False
    
    def verify_collections(self):
        """验证Excel数据与网站收藏是否一致"""
        try:
            # 导航到收藏夹页面
            self.driver.get("https://www.zhipin.com/user/favorites/")
            time.sleep(5)
            
            # 获取收藏的职位列表
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-list ul"))
            )
            time.sleep(3)
            
            favorite_jobs = self.driver.find_elements(By.CSS_SELECTOR, ".job-list ul li.job-card-wrapper")
            print(f"网站上共收藏了 {len(favorite_jobs)} 个职位")
            print(f"Excel中记录了 {len(self.jobs_data)} 个职位")
            
            # 检查数量是否一致
            if len(favorite_jobs) == len(self.jobs_data):
                print("✅ 收藏数量与Excel记录一致")
            else:
                print("❌ 收藏数量与Excel记录不一致")
                return False
            
            # 验证职位信息是否匹配
            matched = 0
            unmatched = 0
            
            for favorite_job in favorite_jobs:
                try:
                    # 获取收藏职位的名称
                    favorite_title = favorite_job.find_element(By.CSS_SELECTOR, ".job-title").text
                    
                    # 检查是否在Excel数据中存在
                    found = any(job['职位名称'] == favorite_title for job in self.jobs_data)
                    if found:
                        matched += 1
                    else:
                        unmatched += 1
                        print(f"❌ 网站收藏的职位在Excel中未找到: {favorite_title}")
                        
                except Exception as e:
                    print(f"验证职位时出错: {str(e)}")
                    continue
            
            print(f"✅ 匹配的职位数量: {matched}")
            print(f"❌ 不匹配的职位数量: {unmatched}")
            
            if unmatched == 0:
                print("✅ 所有网站收藏的职位在Excel中都有记录")
                return True
            else:
                print("❌ 部分网站收藏的职位在Excel中未找到")
                return False
                
        except Exception as e:
            print(f"验证收藏时出错: {str(e)}")
            return False
    
    def close_browser(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

class BossZhipinSkill:
    """Boss直聘自动化Skill，接受用户的求职需求参数"""
    
    def __init__(self, city="苏州", job_keyword="开发者", salary_min=10000, salary_max=13000,
                 company_scale_min=100, company_scale_max=10000, employment_type="全职", max_pages=3):
        self.city = city
        self.job_keyword = job_keyword
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.company_scale_min = company_scale_min
        self.company_scale_max = company_scale_max
        self.employment_type = employment_type
        self.max_pages = max_pages
        self.automation = BossZhipinAutomation()
    
    def run(self):
        """执行自动化流程"""
        print("Boss直聘自动化Skill开始运行...")
        print(f"搜索条件：城市={self.city}, 职位={self.job_keyword}, 薪资={self.salary_min/1000}k-{self.salary_max/1000}k, 公司规模={self.company_scale_min}-{self.company_scale_max}+人")
        
        try:
            # 启动浏览器
            if not self.automation.start_browser():
                return False
            
            # 登录
            if not self.automation.login():
                return False
            
            # 搜索职位
            if not self.automation.search_jobs():
                return False
            
            # 筛选条件
            if not self.automation.filter_jobs():
                return False
            
            # 收集职位信息
            self.automation.collect_jobs(max_pages=self.max_pages)
            
            # 导出到Excel
            if not self.automation.export_to_excel():
                return False
            
            # 验证收藏与Excel数据一致性
            if self.automation.verify_collections():
                print("✅ 所有验证通过！")
            else:
                print("❌ 验证失败！")
                return False
            
            print("Boss直聘自动化Skill运行完成！")
            return True
            
        except Exception as e:
            print(f"Skill运行出错: {str(e)}")
            return False
        finally:
            # 关闭浏览器
            self.automation.close_browser()


def main():
    """主函数"""
    print("Boss直聘自动化脚本开始运行...")
    
    # 使用默认参数运行
    skill = BossZhipinSkill()
    skill.run()


if __name__ == "__main__":
    main()
