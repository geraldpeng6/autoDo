"""
调试图片保存模块
提供图像调试功能，可以在图片上标注匹配位置、置信度等信息。
"""
import cv2
import os
import logging
import datetime
from typing import List, Tuple


def save_debug_image(screenshot, match_positions: List[Tuple[int, int]], template_name: str,
                    template_width: int = 0, template_height: int = 0,
                    scale_x: float = 1.0, scale_y: float = 1.0,
                    threshold: float = 0.8, confidence: float = 0.0,
                    draw_center: bool = False,
                    offset_x: float = 0, offset_y: float = 0,
                    image_type: str = 'match'):  # 'match', 'click', or 'fail'
    """
    保存调试图片
    
    Args:
        screenshot: 屏幕截图（OpenCV格式）
        match_positions (List[Tuple[int, int]]): 匹配位置列表，每个元素为(x, y)坐标
        template_name (str): 模板图片名称
        template_width (int): 模板宽度，默认为0
        template_height (int): 模板高度，默认为0
        scale_x (float): X轴缩放比例，默认为1.0
        scale_y (float): Y轴缩放比例，默认为1.0
        threshold (float): 匹配阈值，默认为0.8
        confidence (float): 匹配置信度，默认为0.0
        draw_center (bool): 是否绘制中心点，默认为False
        offset_x (float): X轴偏移比例，默认为0
        offset_y (float): Y轴偏移比例，默认为0
        image_type (str): 图片类型，可选值：
            - 'match'：匹配成功（绿色标注）
            - 'click'：点击操作（蓝色标注）
            - 'fail'：匹配失败（红色标注）
            - 'success'：一套流程成功
            
    Note:
        - 图片将保存在logs/debug_images/目录下
        - 文件名格式：时间戳_模板名称.png
        - 根据image_type使用不同颜色标注：
          * match: 绿色
          * click: 蓝色
          * fail: 红色
          * success
        - 会在图片上显示匹配置信度
        - 对于点击操作，会额外绘制点击位置的十字线和圆圈
    """
    try:
        # 确保image_type是有效的字符串值
        if not isinstance(image_type, str) or image_type not in ['match', 'click', 'fail', 'success']:
            image_type = 'match'  # 默认值
            
        # 确保template_name是有效的字符串值
        template_name = str(template_name)
        
        # 创建调试图片目录
        debug_dir = os.path.join('logs', 'debug_images', image_type)
        os.makedirs(debug_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        template_basename = os.path.splitext(os.path.basename(template_name))[0]
        filename = f"{timestamp}_{template_basename}.png"
        filepath = os.path.join(debug_dir, filename)
        
        # 复制截图
        debug_image = screenshot.copy()
        if image_type == 'success':
            cv2.imwrite(filepath, debug_image)
            log_msg = f"已保存{image_type}，大功告成，图片: {filepath}"
            return  # 无需继续处理，直接返回
        # 在图片上绘制匹配位置
        for pos in match_positions:
            x, y = pos
            
            # 计算实际位置（考虑缩放和偏移）
            actual_x = int(x * scale_x)
            actual_y = int(y * scale_y)
            
            # 根据图片类型选择颜色
            color = {
                'match': (0, 255, 0),  # 绿色
                'click': (255, 0, 0),  # 蓝色
                'fail': (0, 0, 255)    # 红色
            }.get(image_type, (0, 255, 0))  # BGR格式
        
            # 绘制矩形
            logging.info(f"绘制矩形: {actual_x}, {actual_y}, {template_width}, {template_height}")
            cv2.rectangle(debug_image,
                        (actual_x, actual_y),
                        (actual_x + template_width, actual_y + template_height),
                        color, 2)
            
            # 在矩形上方显示匹配度
            conf_text = f"{confidence:.3f}"  # 只显示数字，更简洁
            font_scale = 1.0  # 增大字体大小
            thickness = 2  # 增加字体粗细
            text_size = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            text_x = actual_x
            text_y = actual_y - 10  # 将文字放在矩形上方10个像素
            # 绘制文字
            cv2.putText(debug_image, conf_text,
                      (text_x, text_y),
                      cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
            
            # 对于点击操作，绘制点击位置
            if image_type == 'click':
                # 计算点击位置（考虑模板大小和偏移）
                click_x = int(actual_x + template_width * offset_x)
                click_y = int(actual_y + template_height * offset_y)
                
                # 绘制十字线
                line_length = 20  # 增加十字线长度使其更明显
                line_thickness = 2
                
                # 绘制圆圈
                cv2.circle(debug_image, (click_x, click_y), line_length, color, 1)
                
                # 水平线
                cv2.line(debug_image,
                        (click_x - line_length, click_y),
                        (click_x + line_length, click_y),
                        color, line_thickness)
                # 垂直线
                cv2.line(debug_image,
                        (click_x, click_y - line_length),
                        (click_x, click_y + line_length),
                        color, line_thickness)
                
                # 在点击位置附近添加坐标文本
                text = f"Click: ({click_x}, {click_y})"
                cv2.putText(debug_image, text, 
                          (click_x + 10, click_y - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 保存图片
        cv2.imwrite(filepath, debug_image)
        
        # 记录日志
        log_msg = f"已保存{image_type}调试图片: {filepath}"
        if image_type == 'match':
            log_msg += f": 匹配位置: {match_positions}"
        elif image_type == 'click':
            click_x = int(actual_x + template_width * offset_x)
            click_y = int(actual_y + template_height * offset_y)
            log_msg += f": 点击位置: ({click_x}, {click_y})"
        elif image_type == 'fail':
            log_msg += f": 失败匹配位置: {match_positions}"
        
        logging.info(log_msg)
        
    except Exception as e:
        logging.error(f"保存调试图片失败: {str(e)}")
