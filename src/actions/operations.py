"""
操作处理模块
提供了一系列用于处理自动化操作的函数，包括文本输入、页面移动等。
"""
import pyautogui
import logging
import random
import platform
import time
from typing import Any, Dict, List, Union
import pyperclip


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

def handle_operation(operation: Dict[str, Any]) -> None:
    """
    处理单个操作
    
    Args:
        operation (Dict[str, Any]): 操作字典，支持以下格式：
            - {'input': value}: 输入文本，value可以是字符串或random(min,max)格式
            - {'move': [x, y]}: 移动页面，x和y为移动比例
            
    Raises:
        ValueError: 当操作类型未知或参数格式错误时抛出
        Exception: 当操作执行失败时抛出
        
    Note:
        - 支持随机数生成，格式为'random(min,max)'
        - 每个操作后会有0.5秒延时
    """
    try:
        for op_type, value in operation.items():
            if op_type == 'input':
                if isinstance(value, str) and value.startswith('random('):
                    # 处理random(min,max)格式
                    nums = value.strip('random()').split(',')
                    min_val, max_val = map(float, nums)
                    input_text(f"{random.uniform(min_val, max_val):.3f}")
                else:
                    input_text(str(value))
            elif op_type == 'move':
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    move_page(value[0], value[1])
                else:
                    raise ValueError(f"move操作需要[x,y]格式的参数，收到: {value}")
            else:
                raise ValueError(f"未知的操作类型: {op_type}")
        
        # 每个操作后短暂延时
        time.sleep(0.5)
    except Exception as e:
        logging.error(f"操作执行失败: {str(e)}")
        raise


def handle_operations(operations: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
    """
    处理操作列表
    
    Args:
        operations: 单个操作字典或操作字典列表，每个字典格式如下：
            - {'input': value}: 输入文本
            - {'move': [x, y]}: 移动页面
            
    Note:
        - 如果传入单个操作字典，会自动转换为列表处理
        - 按顺序执行每个操作
    """
    if isinstance(operations, dict):
        operations = [operations]
    
    for operation in operations:
        handle_operation(operation)
