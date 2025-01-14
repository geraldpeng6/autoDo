"""
调试图片保存模块
"""
import cv2
import os
import logging
import datetime
from typing import List, Tuple


def save_debug_image(screenshot, match_positions: List[Tuple[int, int]], template_name: str,
                    template_width: int = 0, template_height: int = 0,
                    scale_x: float = 1.0, scale_y: float = 1.0,
                    threshold: float = 0.8, debug_level: int = 0,
                    draw_center: bool = False,
                    offset_x: float = 0, offset_y: float = 0,
                    is_click: bool = False):
    """
    保存调试图片
    
    Args:
        screenshot: 屏幕截图
        match_positions: 匹配位置列表
        template_name: 模板名称
        template_width: 模板宽度
        template_height: 模板高度
        scale_x: X轴缩放比例
        scale_y: Y轴缩放比例
        threshold: 匹配阈值
        debug_level: 调试级别
        draw_center: 是否绘制中心点
        offset_x: X轴偏移比例
        offset_y: Y轴偏移比例
        is_click: 是否是点击操作的调试图片
    """
    try:
        # 创建调试图片目录
        if is_click:
            debug_dir = os.path.join('logs', 'debug_images', 'click')
        else:
            debug_dir = os.path.join('logs', 'debug_images', 'match')
        os.makedirs(debug_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        template_basename = os.path.splitext(os.path.basename(template_name))[0]
        filename = f"{template_basename}_{timestamp}.png"
        filepath = os.path.join(debug_dir, filename)
        
        # 复制截图
        debug_image = screenshot.copy()
        
        # 在每个匹配位置绘制矩形和中心点
        for pos in match_positions:
            if not pos:
                continue
                
            x, y = pos
            
            # 绘制矩形
            cv2.rectangle(debug_image, (x, y),
                         (x + template_width, y + template_height),
                         (0, 255, 0), 2)
                         
            if draw_center:
                # 计算实际点击位置
                click_x = int(x + template_width * (0.5 + offset_x))
                click_y = int(y + template_height * (0.5 + offset_y))
                
                # 绘制十字线
                line_length = 10
                cv2.line(debug_image,
                         (click_x - line_length, click_y),
                         (click_x + line_length, click_y),
                         (0, 0, 255), 2)
                cv2.line(debug_image,
                         (click_x, click_y - line_length),
                         (click_x, click_y + line_length),
                         (0, 0, 255), 2)
                         
        # 添加调试信息
        if debug_level > 0:
            info_text = f"Scale: ({scale_x:.2f}, {scale_y:.2f})"
            info_text += f" Threshold: {threshold:.2f}"
            info_text += f" Offset: ({offset_x:.2f}, {offset_y:.2f})"
            cv2.putText(debug_image, info_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
        # 保存图片
        cv2.imwrite(filepath, debug_image)
        logging.info(f"保存调试图片: {filepath}")
        
    except Exception as e:
        logging.error(f"保存调试图片失败: {str(e)}")
        return
