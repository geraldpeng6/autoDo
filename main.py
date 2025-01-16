#!/usr/bin/env python3
"""
自动化操作主程序
"""
import os
import time
import logging
import json

from src.utils.logging_config import setup_logging
from src.image.template_matcher import find_template
from src.actions.metamask import handle_metamask_process
from src.actions.operations import handle_operations
from src.config import settings
import pyautogui
def process_templates(template_data):
    """处理模板文件中的图片"""
    time.sleep(3)
    w = 0
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
            if any('wait' in img for img in template_images):
                wait_time = 10
            # 查找并点击图片
            match_pos, template_size = find_template(template_images)
            
            # 特殊处理MetaMask登录情况
            if any('metamask' in img for img in template_images):
                if any('wait' in img for img in template_images):
                    w = 10
                if not handle_metamask_process(match_pos, template_size, w):
                    raise RuntimeError()
                continue
            
            if not match_pos:
                error_msg = f"无法找到图片: {template_images}"
                logging.error(error_msg)
                raise RuntimeError(error_msg)
            
            # 执行操作
            operations = template.get('operations', [])
            handle_operations(operations, match_pos=match_pos, template_size=template_size)
            
            time.sleep(1)
        
        logging.info("程序成功完成所有操作")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}", exc_info=True)
        raise


def workflow(workjson):
    """主函数"""
    try:
        # 确保在项目根目录下运行
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        # 设置日志
        log_file = setup_logging()
        logging.info("程序开始运行")
        logging.info(f"日志文件位置: {log_file}")
        # 要用请新建一个json
        workjson = workjson

        # 获取缩放信息
        screen_width, screen_height = pyautogui.size()
        scale_x =  settings.display_width/screen_width
        scale_y =  settings.display_height/screen_height

        print(f"Screen resolution: {screen_width}x{screen_height}")
        print(f"Scale factors: x={scale_x:.2f}, y={scale_y:.2f}")

        settings.scale_x = scale_x
        settings.scale_y = scale_y
        
        # 读取JSON模板文件
        with open(workjson, 'r') as json_file:
            templates_data = json.load(json_file)
        process_templates(templates_data)
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    # 要用请新建一个json
    workjson_path = ["./json/verio.json",
                     ]
    settings.display_width = 2560
    settings.display_height = 1600

    for workjson in workjson_path:
        workflow(workjson)
