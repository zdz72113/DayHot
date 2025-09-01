#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定时任务调度器
用于每日自动执行GitHub trending和ProductHunt抓取任务
"""

import schedule
import time
import logging
from datetime import datetime
from main import DayHotTool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DayHotScheduler:
    """每日热门工具定时任务调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.tool = None
        self.is_running = False
    
    def initialize_tool(self):
        """初始化工具"""
        try:
            self.tool = DayHotTool()
            logger.info("每日热门工具初始化成功")
        except Exception as e:
            logger.error(f"工具初始化失败: {e}")
            raise
    
    def daily_task(self):
        """每日任务"""
        try:
            logger.info("开始执行每日定时任务")
            
            if not self.tool:
                self.initialize_tool()
            
            # 执行任务
            success = self.tool.run_daily_task()
            
            if success:
                logger.info("每日定时任务执行成功")
            else:
                logger.error("每日定时任务执行失败")
                
        except Exception as e:
            logger.error(f"执行每日定时任务时出错: {e}")
    
    def start_scheduler(self, time_str: str = "05:00"):
        """
        启动调度器
        
        Args:
            time_str: 每日执行时间，格式为 "HH:MM"
        """
        try:
            logger.info(f"启动每日热门工具定时任务调度器，执行时间: {time_str}")
            
            # 初始化工具
            self.initialize_tool()
            
            # 设置每日任务
            schedule.every().day.at(time_str).do(self.daily_task)
            
            # 立即执行一次（用于测试）
            logger.info("立即执行一次任务进行测试...")
            self.daily_task()
            
            self.is_running = True
            
            # 运行调度器
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止调度器")
            self.stop_scheduler()
        except Exception as e:
            logger.error(f"调度器运行出错: {e}")
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        logger.info("调度器已停止")
    
    def add_custom_schedule(self, schedule_func, time_str: str):
        """
        添加自定义调度任务
        
        Args:
            schedule_func: 要执行的函数
            time_str: 执行时间
        """
        schedule.every().day.at(time_str).do(schedule_func)
        logger.info(f"添加自定义调度任务: {time_str}")

def main():
    """主函数"""
    try:
        # 创建调度器
        scheduler = DayHotScheduler()
        
        # 启动调度器，设置每日早上5点执行
        scheduler.start_scheduler("05:00")
        
    except Exception as e:
        logger.error(f"调度器启动失败: {e}")
        exit(1)

if __name__ == "__main__":
    main()

