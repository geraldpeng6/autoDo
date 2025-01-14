"""
模板匹配模块
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
                 threshold: float = 0.8,
                 max_wait_time: float = 10.0,
                 check_interval: float = 0.1) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    """
    在屏幕上查找模板图片
    
    Args:
        template_paths: 模板图片路径列表
        threshold: 匹配阈值
        max_wait_time: 最大等待时间（秒）
        check_interval: 检查间隔（秒）
        
    Returns:
        tuple: (匹配位置(x,y), 模板大小(width,height))，如果没找到则返回(None, None)
    """
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # 获取屏幕截图
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 遍历所有模板
            for template_path in template_paths:
                try:
                    # 读取模板图片
                    template = cv2.imread(template_path)
                    if template is None:
                        logging.error(f"无法读取模板图片: {template_path}")
                        continue
                        
                    # 获取模板尺寸
                    template_height, template_width = template.shape[:2]
                    
                    # 模板匹配
                    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val >= threshold:
                        match_pos = (max_loc[0], max_loc[1])
                        template_size = (template_width, template_height)
                        
                        # 保存debug图片
                        threading.Thread(target=save_debug_image,
                                      args=(screenshot, [match_pos], template_path,
                                            template_width, template_height, 1.0, 1.0,
                                            threshold, 0, False, 0, 0, False),
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
            
    logging.info(f"未找到模板: {template_paths}")
    return None, None
