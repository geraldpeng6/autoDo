"""
模板匹配模块
提供图像模板匹配功能，支持多模板匹配和调试图片保存。
"""
import cv2
import numpy as np
import pyautogui
import logging
import time
import threading
from typing import List, Tuple, Optional

from src.image.debug_image import save_debug_image


def find_template(template_paths: List[str],
                 threshold: float = 0.7,
                 max_wait_time: float = 5.0,
                 check_interval: float = 0.1) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    """
    在屏幕上查找模板图片
    
    Args:
        template_paths (List[str]): 模板图片路径列表，按优先级排序
        threshold (float): 匹配阈值，范围[0,1]，值越大要求匹配度越高
        max_wait_time (float): 最大等待时间（秒）
        check_interval (float): 检查间隔（秒）
        
    Returns:
        tuple: 包含两个元素：
            - 匹配位置 (x,y)，未找到则为None
            - 模板大小 (width,height)，未找到则为None
            
    Note:
        - 支持多个模板，会返回匹配度最高的结果
        - 会自动保存调试图片，包括匹配结果和点击位置
        - 使用OpenCV的模板匹配算法
        - 如果超时未找到匹配结果，返回(None, None)
    """
    start_time = time.time()
    best_match = None  # (max_val, match_pos, template_size, screenshot, template_path)
    
    while time.time() - start_time < max_wait_time:
        try:
            # 获取屏幕截图
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 遍历所有模板
            for template_path in template_paths:
                try:
                    logging.info(f"处理模板: \n{template_path}")

                    # 读取模板图片
                    template = cv2.imread(template_path)
                    if template is None:
                        logging.error(f"无法读取模板图片: {template_path}")
                        raise Exception(f"无法读取模板图片: {template_path}")
                        
                    # 获取模板尺寸
                    template_height, template_width = template.shape[:2]
                    
                    # 模板匹配
                    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    # 更新最佳匹配
                    if best_match is None or max_val > best_match[0]:
                        match_pos = (max_loc[0], max_loc[1])
                        template_size = (template_width, template_height)
                        best_match = (max_val, match_pos, template_size, screenshot, template_path)
                    
                    if max_val >= threshold:
                        match_pos = (max_loc[0], max_loc[1])
                        template_size = (template_width, template_height)
                        
                        # 保存匹配成功的debug图片
                        threading.Thread(target=save_debug_image,
                                      kwargs={
                                          'screenshot': screenshot,
                                          'match_positions': [match_pos],
                                          'template_name': template_path,
                                          'template_width': template_width,
                                          'template_height': template_height,
                                          'scale_x': 1.0,
                                          'scale_y': 1.0,
                                          'threshold': threshold,
                                          'confidence': max_val,
                                          'draw_center': False,
                                          'offset_x': 0,
                                          'offset_y': 0,
                                          'image_type': 'match'
                                      },
                                      daemon=True).start()
                        
                        # 保存点击位置的debug图片
                        click_offset_x = 0.5  # 中心点X偏移
                        click_offset_y = 0.5  # 中心点Y偏移
                        threading.Thread(target=save_debug_image,
                                      kwargs={
                                          'screenshot': screenshot,
                                          'match_positions': [match_pos],
                                          'template_name': template_path,
                                          'template_width': template_width,
                                          'template_height': template_height,
                                          'scale_x': 1.0,
                                          'scale_y': 1.0,
                                          'threshold': threshold,
                                          'confidence': max_val,
                                          'draw_center': True,
                                          'offset_x': click_offset_x,
                                          'offset_y': click_offset_y,
                                          'image_type': 'click'
                                      },
                                      daemon=True).start()
                        
                        logging.info(f"找到模板 {template_path}")
                        logging.info(f"匹配位置: {match_pos}, 匹配度: {max_val:.3f}")
                        return match_pos, template_size
                        
                except Exception as e:
                    logging.error(f"处理模板 {template_path} 失败: {str(e)}")
                    continue
                    
            time.sleep(check_interval)
            
        except Exception as e:
            logging.error(f"模板匹配失败: {str(e)}")
            return None, None
    
    # 如果没找到，保存最佳匹配的调试图片
    if best_match:
        max_val, match_pos, template_size, screenshot, template_path = best_match
        threading.Thread(target=save_debug_image,
                      kwargs={
                          'screenshot': screenshot,
                          'match_positions': [match_pos],
                          'template_name': template_path,
                          'template_width': template_size[0],
                          'template_height': template_size[1],
                          'scale_x': 1.0,
                          'scale_y': 1.0,
                          'threshold': threshold,
                          'confidence': max_val,
                          'draw_center': False,
                          'offset_x': 0,
                          'offset_y': 0,
                          'image_type': 'fail'
                      },
                      daemon=True).start()
        logging.info(f"未找到模板: {template_paths}")
        logging.info(f"最佳匹配度: {max_val:.3f}")
    
    return None, None
