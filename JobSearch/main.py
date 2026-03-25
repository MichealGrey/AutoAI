import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from JobSearch.config.jobConfig import JobSearchConfig
from JobSearch.controllers.bossZhipin import BossZhipinController
from loguru import logger
from datetime import datetime

def setup_logger():
    log_path = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_path, exist_ok=True)
    
    logger.add(
        os.path.join(log_path, f"job_search_{datetime.now().strftime('%Y%m%d')}.log"),
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )

def search_jobs(
    city: str = "苏州",
    salary_min: int = 10,
    salary_max: int = 13,
    company_size_min: int = 100,
    company_size_max: int = 10000,
    keyword: str = "开发者",
    max_jobs: int = 50
):
    """
    Boss直聘职位搜索与收藏
    
    Args:
        city: 城市
        salary_min: 最低薪资(K)
        salary_max: 最高薪资(K)
        company_size_min: 最小公司规模
        company_size_max: 最大公司规模
        keyword: 搜索关键词
        max_jobs: 最大收集数量
    
    Returns:
        tuple: (职位列表, Excel文件路径)
    """
    setup_logger()
    
    config = JobSearchConfig(
        city=city,
        salary_min=salary_min,
        salary_max=salary_max,
        company_size_min=company_size_min,
        company_size_max=company_size_max,
        keyword=keyword,
        max_jobs=max_jobs
    )
    
    logger.info(f"开始职位搜索任务: {config}")
    
    controller = BossZhipinController(config)
    jobs, filepath = controller.run()
    
    if jobs:
        logger.info(f"任务完成! 共收集 {len(jobs)} 个职位")
        logger.info(f"Excel文件: {filepath}")
    else:
        logger.warning("未收集到任何职位")
    
    return jobs, filepath

if __name__ == "__main__":
    jobs, filepath = search_jobs(
        city="苏州",
        salary_min=10,
        salary_max=13,
        company_size_min=100,
        company_size_max=10000,
        keyword="开发者",
        max_jobs=50
    )
    
    if jobs:
        print(f"\n{'='*60}")
        print(f"任务完成!")
        print(f"共收集 {len(jobs)} 个职位")
        print(f"Excel文件: {filepath}")
        print(f"{'='*60}\n")
        
        print("职位列表预览:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"{i}. {job['title']} - {job['company']} ({job['salary']})")
        if len(jobs) > 5:
            print(f"... 还有 {len(jobs)-5} 个职位")
