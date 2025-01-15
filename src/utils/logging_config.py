"""
日志配置模块
提供日志系统的配置功能，支持同时输出到文件和控制台。
"""
import os
import logging
import datetime


def setup_logging():
    """
    设置日志配置
    
    Returns:
        str: 日志文件路径
        
    Note:
        - 日志文件保存在logs/log/目录下
        - 文件名格式：auto_do_年月日_时分秒.log
        - 日志级别：INFO
        - 日志格式：时间 - 级别 - 消息
        - 同时输出到文件和控制台
        - 时间格式：年-月-日 时:分:秒
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
