from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class JobSearchConfig:
    city: str = "苏州"
    salary_min: int = 10
    salary_max: int = 13
    company_size_min: int = 100
    company_size_max: int = 10000
    job_type: str = "全职"
    keyword: str = "开发者"
    max_jobs: int = 50
    output_path: str = None
    
    def __post_init__(self):
        if self.output_path is None:
            self.output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(self.output_path, exist_ok=True)

BOSS_URL = "https://www.zhipin.com/"

SALARY_OPTIONS = {
    "1-2": "1-2K",
    "2-3": "2-3K", 
    "3-5": "3-5K",
    "5-8": "5-8K",
    "8-10": "8-10K",
    "10-15": "10-15K",
    "15-25": "15-25K",
    "25-50": "25-50K",
    "50+": "50K以上"
}

COMPANY_SIZE_OPTIONS = {
    "0-20": "0-20人",
    "20-99": "20-99人",
    "100-499": "100-499人",
    "500-999": "500-999人",
    "1000-9999": "1000-9999人",
    "10000+": "10000人以上"
}

LOGIN_WAIT_TIMEOUT = 120
PAGE_LOAD_TIMEOUT = 30
SCROLL_PAUSE_TIME = 2
