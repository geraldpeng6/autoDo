"""
屏幕信息处理模块
提供屏幕分辨率和缩放比例相关的功能。
"""
import pyautogui
import logging


def get_screen_info():
    """
    获取屏幕信息
    
    Returns:
        tuple: 包含以下信息：
            - real_width (int): 实际分辨率宽度
            - real_height (int): 实际分辨率高度
            - scaled_width (int): 缩放后分辨率宽度
            - scaled_height (int): 缩放后分辨率高度
            - scale_x (float): X轴缩放比例
            - scale_y (float): Y轴缩放比例
            
    Raises:
        Exception: 获取屏幕信息失败时抛出
        
    Note:
        - 实际分辨率是物理显示器的分辨率
        - 缩放后分辨率是设置中的显示分辨率
        - 缩放比例 = 实际分辨率 / 设置分辨率
    """
    try:
        # 获取实际分辨率
        real_width, real_height = pyautogui.size()
        
        # 设置中的显示分辨率（可以通过配置文件或环境变量设置）
        # 例如: 2560x1600
        from ..config import settings
        scaled_width = settings.display_width if hasattr(settings, 'display_width') else 2560
        scaled_height = settings.display_height if hasattr(settings, 'display_height') else 1600
        
        # 计算缩放比例
        scale_x =  scaled_width/real_width
        scale_y =  scaled_height/real_height
        
        logging.info(f"工具分辨率: {real_width}x{real_height}")
        logging.info(f"显示屏幕分辨率: {scaled_width}x{scaled_height}")
        logging.info(f"缩放比例 - X轴: {scale_x:.3f}, Y轴: {scale_y:.3f}")
        
        return real_width, real_height, scaled_width, scaled_height, scale_x, scale_y
        
    except Exception as e:
        logging.error(f"获取屏幕信息失败: {str(e)}")
        raise
