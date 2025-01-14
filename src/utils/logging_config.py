"""
日志配置模块
"""
import os
import logging
import datetime


def setup_logging():
    """
    设置日志配置
    """
    # 创建日志目录
    log_dir = os.path.join('logs', 'log')
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'auto_do_{timestamp}.log')
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logging.info(f'日志文件创建于: {log_file}')
    return log_file
