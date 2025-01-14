"""
鼠标操作模块
"""
import time
import pyautogui
import logging
import numpy as np
import cv2
import threading
from src.config import settings
from src.image.debug_image import save_debug_image


def click_position(pos, size, scale_x=settings.scale_x, scale_y=settings.scale_y, offset_x=0, offset_y=0):
    """
    点击指定位置
    
    Args:
        pos: 位置坐标 (x, y)
        size: 大小 (width, height)
        scale_x: X轴缩放比例
        scale_y: Y轴缩放比例
        offset_x: X轴偏移比例
        offset_y: Y轴偏移比例
        
    Returns:
        bool: 点击是否成功
    """
    try:
        if not pos or not size:
            return False
        
        x, y = pos
        width, height = size
        
        # 计算实际点击位置（考虑缩放和偏移）
        # 由于模板匹配是在实际分辨率下进行的，需要将坐标除以缩放比例
        click_x = (x + width * (0.5 + offset_x)) / scale_x
        click_y = (y + height * (0.5 + offset_y)) / scale_y
        
        logging.info(f"原始坐标: ({x}, {y}), 大小: {width}x{height}")
        logging.info(f"缩放比例: X={scale_x:.3f}, Y={scale_y:.3f}")
        logging.info(f"偏移比例: X={offset_x:.3f}, Y={offset_y:.3f}")
        logging.info(f"最终点击位置: ({click_x:.1f}, {click_y:.1f})")
        
        # 保存debug图片
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        threading.Thread(target=save_debug_image, args=(screenshot, [(x, y)], "click_position",
                                                      width, height, scale_x, scale_y, 1.0, 0, True,
                                                      offset_x, offset_y, True), daemon=True).start()
        
        # 执行点击
        pyautogui.moveTo(click_x, click_y, duration=0.1)
        pyautogui.click()
        return True
        
    except Exception as e:
        logging.error(f"点击位置失败: {str(e)}")
        return False
