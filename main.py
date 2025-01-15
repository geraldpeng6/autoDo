#!/usr/bin/env python3
"""
自动化操作主程序
"""
import os
import time
import logging
import json

from src.utils.logging_config import setup_logging
from src.utils.screen import get_screen_info
from src.image.template_matcher import find_template
from src.actions.mouse import click_position
from src.actions.metamask import handle_metamask_process
from src.actions.operations import handle_operation, handle_operations
from src.config import settings


def process_templates(template_data):
    """处理模板文件中的图片"""
    time.sleep(3)
    try:
        for template in template_data['templates']:
            template_images = template['image']
            # 确保template_images是列表
            if isinstance(template_images, str):
                template_images = [template_images]
            
            offset_x = offset_y = 0
            
            # 获取偏移值（如果有）
            if 'offset' in template:
                offset_x = template['offset'][0]
                offset_y = template['offset'][1]
            
            # 查找并点击图片
            match_pos, template_size = find_template(template_images)
            
            # 特殊处理MetaMask登录情况
            if any('metamask' in img for img in template_images):
                if not handle_metamask_process(match_pos, template_size):
                    raise RuntimeError()
                continue
            
            # 点击位置
            if not match_pos or not click_position(match_pos, template_size,
                                                 settings.scale_x,
                                                 settings.scale_y,
                                                 offset_x=offset_x,
                                                 offset_y=offset_y):
                error_msg = f"无法找到或点击图片: {template_images}"
                logging.error(error_msg)
                raise RuntimeError(error_msg)
            
            # 执行额外操作（如果有）
            if 'operation' in template:
                handle_operation({'input': template['operation']})
            elif 'operations' in template:
                handle_operations(template['operations'])
            
            time.sleep(1)
        
        time.sleep(10)  # 等待页面加载完成
        logging.info("程序成功完成所有操作")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}", exc_info=True)
        raise


def main():
    """主函数"""
    try:
        # 确保在项目根目录下运行
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        # 设置日志
        log_file = setup_logging()
        logging.info("程序开始运行")
        logging.info(f"日志文件位置: {log_file}")
        
        # 获取屏幕信息
        _, _, _, _, scale_x, scale_y = get_screen_info()
        settings.scale_x = scale_x
        settings.scale_y = scale_y
        
        # 读取JSON模板文件
        with open('/Users/jiale/Documents/code/autoDo/verio.json', 'r') as json_file:
            templates_data = json.load(json_file)
        process_templates(templates_data)
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
