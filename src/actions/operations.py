"""
操作处理模块
提供了一系列用于处理自动化操作的函数，包括文本输入、页面移动等。
"""
import pyautogui
import logging
import random
import platform
import time
from typing import Any, Dict, List, Union, Optional, Tuple
import pyperclip
from ..config import settings
from .mouse import click_position


def input_text(text: str) -> None:
    """
    输入文本，使用剪贴板粘贴方式
    
    Args:
        text (str): 要输入的文本内容
        
    Raises:
        Exception: 当输入文本失败时抛出异常
        
    Note:
        - 会先清除当前选中的文本
        - 使用系统剪贴板进行粘贴
        - 会保存并恢复原始剪贴板内容
    """
    try:
        # 全选并删除现有文本
        if platform.system() == 'Darwin':
            pyautogui.hotkey('command', 'a')
        else:
            pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        
        # 通过剪贴板粘贴文本
        original_clipboard = pyperclip.paste()
        pyperclip.copy(text)
        if platform.system() == 'Darwin':
            pyautogui.hotkey('command', 'v')
        else:
            pyautogui.hotkey('ctrl', 'v')
        pyperclip.copy(original_clipboard)
        
        logging.info(f"输入文本: {text}")
    except Exception as e:
        logging.error(f"输入文本失败: {str(e)}")
        raise


def move_page(x: float, y: float) -> None:
    """
    移动页面，控制页面滚动
    
    Args:
        x (float): X轴移动比例，范围[-1.0, 1.0]，负值向左，正值向右
        y (float): Y轴移动比例，范围[-1.0, 1.0]，负值向上，正值向下
        
    Raises:
        Exception: 当移动页面失败时抛出异常
        
    Note:
        - 移动距离由屏幕尺寸和比例值共同决定
        - x=0.5表示向右移动屏幕宽度的50%
        - y=0.5表示向下移动屏幕高度的50%
    """
    try:
        screen_width, screen_height = pyautogui.size()
        move_x = int(screen_width * x)
        move_y = int(screen_height * y)
        
        pyautogui.scroll(move_y)
        if move_x != 0:
            pyautogui.hscroll(move_x)
            
        logging.info(f"移动页面: x={x:.2f}, y={y:.2f}")
    except Exception as e:
        logging.error(f"移动页面失败: {str(e)}")
        raise


def handle_click(click_data: Dict[str, Any], match_pos: Tuple[int, int], template_size: Tuple[int, int]) -> bool:
    """
    处理点击操作
    
    Args:
        click_data: 点击配置字典，支持以下格式：
            - click_count: 点击次数，默认1
            - offset: [x, y] 偏移量，默认[0, 0]
            - random: {x: float, y: float} x和y方向的随机范围，默认都为0
            
    Returns:
        bool: 点击是否成功
    """
    try:
        # 提取参数
        click_count = click_data.get('click_count', 1)
        offset = click_data.get('offset', [0, 0])
        random_range = click_data.get('random', {'x': 0, 'y': 0})
        
        # 计算随机偏移
        random_x = random_range.get('x', 0)
        random_y = random_range.get('y', 0)
        
        return click_position(
            pos=match_pos,
            size=template_size,
            scale_x=settings.scale_x,
            scale_y=settings.scale_y,
            offset_x=offset[0],
            offset_y=offset[1],
            click_count=click_count,
            random_click=[random_x, random_y]
        )
        
    except Exception as e:
        logging.error(f"点击操作失败: {str(e)}")
        return False


def handle_operation(operation: Dict[str, Any], match_pos: Optional[Tuple[int, int]] = None, template_size: Optional[Tuple[int, int]] = None) -> None:
    """
    处理单个操作
    
    Args:
        operation: 操作字典，支持以下格式：
            - {'input': value}: 输入文本，value可以是字符串或random(min,max)格式
            - {'move': [x, y]}: 移动页面，x和y为移动比例
            - {'click': {...}}: 点击操作，包含click_count、offset和random配置
            - {'keyboard': key}: 键盘操作，支持单个按键或按键列表
        match_pos: 匹配位置坐标，用于点击操作
        template_size: 模板大小，用于点击操作
            
    Raises:
        ValueError: 当操作类型未知或参数格式错误时抛出
        Exception: 当操作执行失败时抛出
    """
    try:
        if 'input' in operation:
            # 处理input操作
            if isinstance(operation['input'], str) and operation['input'].startswith('random('):
                # 处理random(min,max)格式
                nums = operation['input'].strip('random()').split(',')
                min_val, max_val = map(float, nums)
                input_text(f"{random.uniform(min_val, max_val):.3f}")
            else:
                input_text(str(operation['input']))
        elif 'move' in operation:
            move_page(*operation['move'])
        elif 'click' in operation:
            if not match_pos or not template_size:
                raise ValueError("点击操作需要提供match_pos和template_size参数")
            if not handle_click(operation['click'], match_pos, template_size):
                raise Exception("点击操作失败")
        elif 'keyboard' in operation:
            keys = operation['keyboard']
            if isinstance(keys, str):
                keys = [keys]
            for key in keys:
                pyautogui.press(key)
                time.sleep(0.1)
        else:
            raise ValueError(f"未知的操作类型: {operation}")
            
        time.sleep(0.5)
        
    except Exception as e:
        logging.error(f"操作执行失败: {str(e)}")
        raise


def handle_operations(operations: Union[Dict[str, Any], List[Dict[str, Any]]], match_pos: Optional[Tuple[int, int]] = None, template_size: Optional[Tuple[int, int]] = None) -> None:
    """
    处理操作列表
    
    Args:
        operations: 单个操作字典或操作字典列表
        match_pos: 匹配位置坐标，用于点击操作
        template_size: 模板大小，用于点击操作
    """
    if not isinstance(operations, list):
        operations = [operations]

    # 检查是否有click操作
    has_click = any('click' in op for op in operations)
    
    # 如果没有click操作且match_pos存在，添加默认点击
    if not has_click and match_pos and template_size:
        default_click = {'click': {'click_count': 1}}
        operations.insert(0, default_click)  # 插入到列表开头
        
    for operation in operations:
        handle_operation(operation, match_pos, template_size)
