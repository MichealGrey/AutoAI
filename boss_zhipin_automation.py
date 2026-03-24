#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘自动化脚本
功能：自动登录、搜索职位、收藏符合条件的职位、导出Excel
"""

import time
import json
import logging
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('boss_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class JobInfo:
    """职位信息数据类"""
    job_title: str
    company_name: str
    salary: str
    location: str
    company_size: str
    job_tags: str
    job_description: str
    job_url: str
    collected_at: str


class BossZhipinAutomation:
    """Boss直聘自动化类"""
    
    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless
        self.jobs_collected: List[JobInfo] = []
        self.wait_timeout = 15
        self.implicit_wait = 5
        
    def setup_driver(self):
        """初始化Chrome浏览器"""
        logger.info("正在初始化浏览器...")
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 添加User-Agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(self.implicit_wait)
            logger.info("浏览器初始化成功")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise
    
    def navigate_to_login(self):
        """导航到首页并处理登录"""
        logger.info("正在访问Boss直聘网站...")
        self.driver.get("https://www.zhipin.com/")
        time.sleep(5)
        
        try:
            # 等待页面加载
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)
            
            # 先尝试查找首页的职位卡片，看是否能直接获取数据
            job_cards = self._find_homepage_job_cards()
            
            if job_cards:
                logger.info(f"首页发现 {len(job_cards)} 个职位卡片，尝试提取信息...")
                # 尝试提取第一个卡片看是否成功（判断是否已登录）
                can_extract = self._try_extract_first_card(job_cards)
                
                if can_extract:
                    logger.info("可以正常提取职位信息，可能已登录或无需登录")
                    return
                else:
                    logger.info("无法提取职位详情，需要登录...")
                    self._click_login_button()
            else:
                logger.info("首页未发现职位卡片，尝试点击职位按钮或登录...")
                # 先尝试点击头部职位按钮
                if not self._click_header_job_button():
                    # 如果失败，尝试登录
                    self._click_login_button()
                    
        except TimeoutException:
            logger.warning("页面加载超时，继续执行...")
    
    def _find_homepage_job_cards(self) -> List:
        """查找首页职位卡片"""
        selectors = [
            "//li[contains(@class, 'job-card')]",
            "//div[contains(@class, 'job-card')]",
            "//div[contains(@class, 'job-list')]//li",
            "//ul[contains(@class, 'job-list')]//li",
            "//div[contains(@class, 'card')]",
            "//div[contains(@class, 'job-item')]",
            "//li[contains(@class, 'job-item')]",
            "//div[contains(@class, 'search-job-result')]//li",
        ]
        
        for selector in selectors:
            try:
                cards = self.driver.find_elements(By.XPATH, selector)
                if cards and len(cards) > 0:
                    logger.info(f"通过选择器找到首页职位卡片: {selector}, 数量: {len(cards)}")
                    return cards
            except:
                continue
        return []
    
    def _try_extract_first_card(self, job_cards) -> bool:
        """尝试提取第一个卡片，验证是否可以正常访问"""
        try:
            if not job_cards:
                return False
            first_card = job_cards[0]
            # 尝试查找职位名称
            title_selectors = [
                ".//span[contains(@class, 'job-name')]",
                ".//a[contains(@class, 'job-name')]",
                ".//span[contains(@class, 'name')]",
                ".//div[contains(@class, 'title')]"
            ]
            for selector in title_selectors:
                try:
                    elem = first_card.find_element(By.XPATH, selector)
                    if elem and elem.text.strip():
                        logger.info(f"成功提取职位: {elem.text.strip()}")
                        return True
                except:
                    continue
            return False
        except Exception as e:
            logger.warning(f"尝试提取卡片失败: {e}")
            return False
    
    def _click_login_button(self):
        """点击登录按钮"""
        logger.info("正在查找登录按钮...")
        
        login_selectors = [
            "//a[contains(text(), '登录')]",
            "//div[contains(text(), '登录')]",
            "//button[contains(text(), '登录')]",
            "//span[contains(text(), '登录')]",
            "//a[@ka='header-login']",
            "//div[@class='nav-figure']",
            "//a[contains(@href, '/login')]",
            "//div[contains(@class, 'login')]",
            "//span[contains(@class, 'login')]"
        ]
        
        login_btn = None
        for selector in login_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    login_btn = elements[0]
                    logger.info(f"找到登录按钮: {selector}")
                    break
            except:
                continue
        
        if login_btn:
            logger.info("点击登录按钮，请扫描二维码完成登录...")
            try:
                login_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", login_btn)
            
            time.sleep(3)
            input("请完成扫码登录，完成后按回车键继续...")
            logger.info("用户确认登录完成")
            time.sleep(3)
        else:
            logger.warning("未找到登录按钮")
    
    def _click_header_job_button(self) -> bool:
        """点击头部导航的职位按钮"""
        logger.info("正在查找头部职位按钮...")
        
        job_nav_selectors = [
            "//a[contains(text(), '职位')]",
            "//span[contains(text(), '职位')]",
            "//div[contains(text(), '职位')]",
            "//a[@ka='header-job']",
            "//li[contains(@class, 'nav-job')]//a",
            "//div[contains(@class, 'nav')]//a[contains(text(), '职位')]",
            "//ul[contains(@class, 'nav')]//a[contains(text(), '职位')]",
            "//a[contains(@href, '/job')]",
        ]
        
        for selector in job_nav_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"找到职位按钮: {selector}")
                    try:
                        elements[0].click()
                    except:
                        self.driver.execute_script("arguments[0].click();", elements[0])
                    time.sleep(5)
                    logger.info("已点击职位按钮")
                    return True
            except:
                continue
        
        logger.warning("未找到头部职位按钮")
        return False
    
    def search_jobs(self, city: str = "苏州", keyword: str = "开发者", 
                   salary_range: str = "10-13K", 
                   company_size: str = "100-10000人"):
        """
        搜索职位
        
        Args:
            city: 城市名称
            keyword: 搜索关键词
            salary_range: 薪资范围
            company_size: 公司规模
        """
        logger.info(f"开始搜索职位: 城市={city}, 关键词={keyword}")
        
        try:
            # 等待页面完全加载
            time.sleep(3)
            
            # 先检查当前是否在职位列表页面
            job_cards = self._find_job_cards()
            if job_cards and len(job_cards) > 0:
                logger.info(f"当前页面已有 {len(job_cards)} 个职位卡片，直接开始收集")
                return
            
            # 尝试多种方式查找搜索框
            search_input = self._find_search_input()
            
            if not search_input:
                logger.warning("无法找到搜索框，尝试直接访问搜索URL")
                # 直接构造搜索URL
                self._backup_search(keyword, city)
            else:
                # 输入搜索关键词
                search_input.clear()
                search_input.send_keys(keyword)
                time.sleep(1)
                
                # 尝试点击搜索按钮或直接回车
                search_btn = self._find_search_button()
                if search_btn:
                    try:
                        search_btn.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", search_btn)
                else:
                    search_input.send_keys(Keys.RETURN)
                
                time.sleep(5)
            
            # 设置筛选条件
            self._apply_filters(city, salary_range, company_size)
            
        except Exception as e:
            logger.error(f"搜索职位时出错: {e}")
            # 不抛出异常，继续尝试其他方式
            logger.info("尝试备用搜索方式...")
            self._backup_search(keyword, city)
    
    def _find_search_input(self):
        """查找搜索输入框 - 多种选择器"""
        selectors = [
            ("//input[@placeholder='搜索职位、公司']", "placeholder方式"),
            ("//input[@placeholder='搜索职位']", "简化placeholder"),
            ("//input[contains(@class, 'search') and @type='text']", "class包含search"),
            ("//input[contains(@class, 'search-input')", "search-input class"),
            ("//input[contains(@class, 'ipt-search')", "ipt-search class"),
            ("//div[contains(@class, 'search-box')]//input", "search-box内的input"),
            ("//input[@name='query']", "name属性"),
            ("//input[@id='search-input']", "id方式"),
            ("//input[contains(@class, 'home-search')", "home-search class"),
        ]
        
        for selector, desc in selectors:
            try:
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info(f"找到搜索框: {desc}")
                return element
            except:
                continue
        
        # 尝试通过CSS选择器
        css_selectors = [
            "input[placeholder*='搜索']",
            ".search-input",
            ".search-box input",
            "input.ipt-search"
        ]
        
        for selector in css_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    logger.info(f"通过CSS找到搜索框: {selector}")
                    return element
            except:
                continue
        
        return None
    
    def _find_search_button(self):
        """查找搜索按钮"""
        selectors = [
            "//button[contains(text(), '搜索')]",
            "//div[contains(text(), '搜索')]",
            "//span[contains(text(), '搜索')]",
            "//a[contains(text(), '搜索')]",
            "//button[contains(@class, 'btn-search')]",
            "//div[contains(@class, 'btn-search')]",
            "//i[contains(@class, 'search-icon')]",
            "//button[@type='submit']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    return elements[0]
            except:
                continue
        return None
    
    def _backup_search(self, keyword: str, city: str):
        """备用搜索方式 - 直接构造URL"""
        try:
            # Boss直聘城市代码映射（部分常用城市）
            city_codes = {
                "苏州": "101210100",
                "上海": "101020100",
                "北京": "101010100",
                "广州": "101280100",
                "深圳": "101280600",
                "杭州": "101210100",
                "南京": "101190100",
                "成都": "101270100",
                "武汉": "101200100",
                "西安": "101110100"
            }
            
            city_code = city_codes.get(city, "101210100")  # 默认苏州
            search_url = f"https://www.zhipin.com/web/geek/job?query={keyword}&city={city_code}"
            
            logger.info(f"使用备用搜索方式，访问: {search_url}")
            self.driver.get(search_url)
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"备用搜索也失败: {e}")
    
    def _apply_filters(self, city: str, salary_range: str, company_size: str):
        """应用筛选条件"""
        logger.info("正在应用筛选条件...")
        
        try:
            # 等待筛选区域加载
            time.sleep(3)
            
            # 点击城市筛选
            self._click_filter_option("城市", city)
            
            # 点击薪资筛选
            self._click_filter_option("薪资", salary_range)
            
            # 点击公司规模筛选
            self._click_filter_option("公司规模", company_size)
            
            logger.info("筛选条件应用完成")
            
        except Exception as e:
            logger.warning(f"应用筛选条件时出错: {e}")
    
    def _click_filter_option(self, filter_name: str, option_text: str):
        """点击筛选选项"""
        try:
            # 先点击筛选器展开
            filter_selectors = [
                f"//span[contains(text(), '{filter_name}')]",
                f"//div[contains(text(), '{filter_name}')]",
                f"//a[contains(text(), '{filter_name}')]",
                f"//span[contains(@class, 'filter') and contains(text(), '{filter_name}')]",
                f"//div[contains(@class, 'filter')]//span[contains(text(), '{filter_name}')]"
            ]
            
            for selector in filter_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    try:
                        elements[0].click()
                    except:
                        self.driver.execute_script("arguments[0].click();", elements[0])
                    time.sleep(2)
                    break
            
            # 点击具体选项
            option_selectors = [
                f"//span[contains(text(), '{option_text}')]",
                f"//a[contains(text(), '{option_text}')]",
                f"//li[contains(text(), '{option_text}')]",
                f"//div[contains(text(), '{option_text}')]",
                f"//span[contains(@class, 'dropdown') and contains(text(), '{option_text}')]"
            ]
            
            for selector in option_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    try:
                        elements[0].click()
                    except:
                        self.driver.execute_script("arguments[0].click();", elements[0])
                    time.sleep(2)
                    logger.info(f"已选择 {filter_name}: {option_text}")
                    return
                    
        except Exception as e:
            logger.warning(f"点击筛选选项失败 {filter_name}-{option_text}: {e}")
    
    def collect_jobs(self, max_pages: int = 3):
        """
        收藏符合条件的职位
        
        Args:
            max_pages: 最大翻页数
        """
        logger.info(f"开始收集职位信息，最多翻页 {max_pages} 页...")
        
        for page in range(max_pages):
            logger.info(f"正在处理第 {page + 1} 页...")
            
            try:
                # 等待职位列表加载
                time.sleep(3)
                
                job_cards = self._find_job_cards()
                
                if not job_cards:
                    logger.warning("未找到职位卡片，可能页面未加载完成")
                    time.sleep(3)
                    job_cards = self._find_job_cards()
                
                logger.info(f"找到 {len(job_cards)} 个职位卡片")
                
                for idx, card in enumerate(job_cards):
                    try:
                        # 提取职位信息
                        job_info = self._extract_job_info(card)
                        
                        if job_info and self._is_job_match_criteria(job_info):
                            # 点击收藏按钮
                            self._click_collect_button(card, job_info)
                            
                    except Exception as e:
                        logger.warning(f"处理第 {idx + 1} 个职位时出错: {e}")
                        continue
                
                # 翻页
                if page < max_pages - 1:
                    if not self._go_to_next_page():
                        logger.info("没有更多页面了")
                        break
                        
            except TimeoutException:
                logger.warning("职位列表加载超时")
                break
            except Exception as e:
                logger.error(f"收集职位时出错: {e}")
                break
        
        logger.info(f"共收集到 {len(self.jobs_collected)} 个符合条件的职位")
    
    def _find_job_cards(self) -> List:
        """查找职位卡片元素"""
        selectors = [
            "//li[contains(@class, 'job-card')]",
            "//div[contains(@class, 'job-card')]",
            "//li[contains(@class, 'job-list-item')]",
            "//div[contains(@class, 'job-list-item')]",
            "//div[contains(@class, 'search-job-result')]//li",
            "//div[contains(@class, 'job-list')]//div[contains(@class, 'item')]",
            "//ul[contains(@class, 'job-list')]//li",
            "//div[contains(@class, 'search-result')]//div[contains(@class, 'card')]"
        ]
        
        for selector in selectors:
            try:
                cards = self.driver.find_elements(By.XPATH, selector)
                if cards:
                    logger.info(f"通过选择器找到职位卡片: {selector}")
                    return cards
            except:
                continue
        
        return []
    
    def _extract_job_info(self, card) -> Optional[JobInfo]:
        """从职位卡片提取信息"""
        try:
            # 职位名称 - 多种可能的选择器
            job_title = self._safe_get_text(card, [
                ".//span[contains(@class, 'job-name')]",
                ".//a[contains(@class, 'job-name')]",
                ".//span[contains(@class, 'name')]",
                ".//a[contains(@class, 'name')]",
                ".//div[contains(@class, 'title')]",
                ".//h3[contains(@class, 'name')]",
                ".//span[@class='job-title']",
                ".//a[contains(@href, '/job_detail')]"
            ])
            
            # 公司名称
            company_name = self._safe_get_text(card, [
                ".//h3[contains(@class, 'company-name')]",
                ".//a[contains(@class, 'company-name')]",
                ".//div[contains(@class, 'company-name')]",
                ".//div[contains(@class, 'company')]//a",
                ".//span[contains(@class, 'company')]",
                ".//a[contains(@href, '/gongsi/')]"
            ])
            
            # 薪资
            salary = self._safe_get_text(card, [
                ".//span[contains(@class, 'salary')]",
                ".//span[contains(text(), 'K')]",
                ".//span[contains(text(), 'k')]",
                ".//span[contains(@class, 'pay')]",
                ".//div[contains(@class, 'salary')]"
            ])
            
            # 地点
            location = self._safe_get_text(card, [
                ".//span[contains(@class, 'job-area')]",
                ".//span[contains(@class, 'area')]",
                ".//span[contains(text(), '·')]",
                ".//div[contains(@class, 'location')]"
            ])
            
            # 公司规模
            company_size = ""
            try:
                company_size = self._safe_get_text(card, [
                    ".//div[contains(@class, 'company-info')]//span",
                    ".//div[contains(@class, 'company-tag')]",
                    ".//span[contains(text(), '人')]",
                    ".//div[contains(@class, 'info')]//span"
                ])
            except:
                pass
            
            # 职位标签
            job_tags = ""
            try:
                tags = card.find_elements(By.XPATH, ".//span[contains(@class, 'tag')] | .//div[contains(@class, 'tag')]")
                job_tags = ", ".join([tag.text for tag in tags if tag.text])
            except:
                pass
            
            # 获取职位详情链接
            job_url = ""
            try:
                job_link = card.find_element(By.XPATH, ".//a[contains(@href, '/job_detail/')]")
                job_url = job_link.get_attribute("href")
            except:
                try:
                    any_link = card.find_element(By.XPATH, ".//a")
                    job_url = any_link.get_attribute("href")
                except:
                    job_url = self.driver.current_url
            
            return JobInfo(
                job_title=job_title or "未知职位",
                company_name=company_name or "未知公司",
                salary=salary or "薪资面议",
                location=location or "地点未知",
                company_size=company_size,
                job_tags=job_tags,
                job_description="",
                job_url=job_url,
                collected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            logger.warning(f"提取职位信息失败: {e}")
            return None
    
    def _safe_get_text(self, parent, selectors: List[str]) -> str:
        """安全地获取元素文本"""
        for selector in selectors:
            try:
                element = parent.find_element(By.XPATH, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        return ""
    
    def _is_job_match_criteria(self, job_info: JobInfo) -> bool:
        """检查职位是否符合条件"""
        try:
            # 检查薪资范围 (1w-1.3w)
            salary_text = job_info.salary
            if 'K' in salary_text or 'k' in salary_text:
                numbers = re.findall(r'\d+', salary_text)
                if numbers:
                    min_salary = int(numbers[0])
                    # 检查是否在10-13K范围内
                    if 10 <= min_salary <= 13:
                        logger.info(f"职位符合薪资条件: {job_info.job_title} - {salary_text}")
                        return True
            
            # 检查公司规模
            size_text = job_info.company_size
            if '人' in size_text:
                numbers = re.findall(r'\d+', size_text)
                if numbers:
                    min_size = int(numbers[0])
                    if 100 <= min_size <= 10000:
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"检查职位条件时出错: {e}")
            return False
    
    def _click_collect_button(self, card, job_info: JobInfo):
        """点击收藏按钮"""
        try:
            # 查找收藏按钮
            collect_selectors = [
                ".//span[contains(@class, 'collect')]",
                ".//i[contains(@class, 'collect')]",
                ".//div[contains(@class, 'collect')]",
                ".//a[contains(@class, 'collect')]",
                ".//span[contains(@class, 'star')]",
                ".//i[contains(@class, 'star')]",
                ".//span[contains(text(), '收藏')]",
                ".//a[contains(text(), '收藏')]",
                ".//button[contains(@class, 'collect')]"
            ]
            
            collect_btn = None
            for selector in collect_selectors:
                try:
                    elements = card.find_elements(By.XPATH, selector)
                    if elements:
                        collect_btn = elements[0]
                        break
                except:
                    continue
            
            if collect_btn:
                # 滚动到元素位置
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", collect_btn)
                time.sleep(1)
                
                # 点击收藏
                try:
                    collect_btn.click()
                except:
                    self.driver.execute_script("arguments[0].click();", collect_btn)
                
                time.sleep(1)
                
                # 添加到已收集列表
                self.jobs_collected.append(job_info)
                logger.info(f"已收藏职位: {job_info.job_title} - {job_info.company_name}")
            else:
                logger.warning(f"未找到收藏按钮: {job_info.job_title}")
                # 即使没找到收藏按钮，也记录职位信息
                self.jobs_collected.append(job_info)
                
        except ElementClickInterceptedException:
            logger.warning(f"收藏按钮被遮挡: {job_info.job_title}")
        except Exception as e:
            logger.error(f"点击收藏按钮失败: {e}")
    
    def _go_to_next_page(self) -> bool:
        """翻页到下一页"""
        try:
            next_selectors = [
                "//a[contains(text(), '下一页')]",
                "//span[contains(text(), '下一页')]",
                "//button[contains(text(), '下一页')]",
                "//a[contains(@class, 'next')]",
                "//span[contains(@class, 'next')]",
                "//li[contains(@class, 'next')]//a",
                "//a[@title='下一页']"
            ]
            
            for selector in next_selectors:
                try:
                    next_btn = self.driver.find_element(By.XPATH, selector)
                    if next_btn.is_enabled() and next_btn.is_displayed():
                        try:
                            next_btn.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(5)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"翻页失败: {e}")
            return False
    
    def export_to_excel(self, filename: Optional[str] = None):
        """
        导出职位信息到Excel
        
        Args:
            filename: Excel文件名，默认为 boss_jobs_YYYYMMDD_HHMMSS.xlsx
        """
        if not filename:
            filename = f"boss_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        logger.info(f"正在导出到Excel: {filename}")
        
        try:
            # 创建工作簿
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "职位列表"
            
            # 设置列标题
            headers = ["序号", "职位名称", "公司名称", "薪资", "工作地点", "公司规模", 
                      "职位标签", "职位描述", "职位链接", "收藏时间"]
            
            # 写入标题
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, size=12)
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            
            # 写入数据
            for idx, job in enumerate(self.jobs_collected, 1):
                ws.cell(row=idx + 1, column=1, value=idx)
                ws.cell(row=idx + 1, column=2, value=job.job_title)
                ws.cell(row=idx + 1, column=3, value=job.company_name)
                ws.cell(row=idx + 1, column=4, value=job.salary)
                ws.cell(row=idx + 1, column=5, value=job.location)
                ws.cell(row=idx + 1, column=6, value=job.company_size)
                ws.cell(row=idx + 1, column=7, value=job.job_tags)
                ws.cell(row=idx + 1, column=8, value=job.job_description)
                ws.cell(row=idx + 1, column=9, value=job.job_url)
                ws.cell(row=idx + 1, column=10, value=job.collected_at)
            
            # 调整列宽
            column_widths = [8, 25, 25, 15, 20, 20, 30, 40, 50, 20]
            for idx, width in enumerate(column_widths, 1):
                ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = width
            
            # 保存文件
            wb.save(filename)
            logger.info(f"Excel导出成功: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            raise
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            logger.info("正在关闭浏览器...")
            self.driver.quit()
            self.driver = None
    
    def run(self, city: str = "苏州", keyword: str = "开发者", 
            salary_range: str = "10-13K", company_size: str = "100-10000人",
            max_pages: int = 3):
        """
        运行完整的自动化流程
        
        Args:
            city: 城市
            keyword: 搜索关键词
            salary_range: 薪资范围
            company_size: 公司规模
            max_pages: 最大翻页数
        """
        try:
            self.setup_driver()
            self.navigate_to_login()
            self.search_jobs(city, keyword, salary_range, company_size)
            self.collect_jobs(max_pages)
            
            if self.jobs_collected:
                excel_file = self.export_to_excel()
                logger.info(f"任务完成！共收集 {len(self.jobs_collected)} 个职位")
                logger.info(f"Excel文件: {excel_file}")
                return excel_file
            else:
                logger.warning("未收集到任何职位信息")
                return None
                
        except Exception as e:
            logger.error(f"运行过程中出错: {e}")
            raise
        finally:
            self.close()


def main():
    """主函数"""
    print("=" * 60)
    print("Boss直聘自动化脚本")
    print("=" * 60)
    print("\n📋 执行流程:")
    print("1. 自动打开Boss直聘首页")
    print("2. 检测首页职位卡片")
    print("   - 如果能提取职位信息 → 直接开始收集")
    print("   - 如果不能提取 → 尝试点击[职位]按钮")
    print("   - 如果仍无法获取 → 提示登录")
    print("3. 搜索并筛选符合条件的职位")
    print("4. 自动收藏职位")
    print("5. 导出Excel表格\n")
    print("⚠️ 注意: 如果弹出登录二维码，请扫码登录后继续\n")
    
    # 创建自动化实例
    automation = BossZhipinAutomation(headless=False)
    
    try:
        # 运行自动化流程
        excel_file = automation.run(
            city="苏州",
            keyword="开发者",
            salary_range="10-13K",
            company_size="100-10000人",
            max_pages=3
        )
        
        if excel_file:
            print(f"\n✅ 任务完成！")
            print(f"📊 Excel文件已生成: {excel_file}")
            print(f"📋 共收集 {len(automation.jobs_collected)} 个职位")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
    finally:
        automation.close()


if __name__ == "__main__":
    main()
