"""
操作处理模块
"""
import pyautogui
import logging
import random
import re
from typing import Any, Dict, Tuple


def input_text(text: str) -> None:
    """
    输入文本
    
    Args:
        text: 要输入的文本
    """
    try:
        pyautogui.typewrite(str(text))
        logging.info(f"输入文本: {text}")
    except Exception as e:
        logging.error(f"输入文本失败: {str(e)}")
        raise


def move_page(offset_x: float, offset_y: float) -> None:
    """
    移动页面
    
    Args:
        offset_x: X轴移动比例 (-1.0 到 1.0)
        offset_y: Y轴移动比例 (-1.0 到 1.0)
    """
    try:
        # 获取屏幕尺寸
        screen_width, screen_height = pyautogui.size()
        # 计算实际移动距离
        move_x = int(screen_width * offset_x)
        move_y = int(screen_height * offset_y)
        
        pyautogui.scroll(move_y)  # 垂直滚动
        if move_x != 0:  # 如果需要水平滚动
            pyautogui.hscroll(move_x)
            
        logging.info(f"移动页面: x={offset_x:.2f}, y={offset_y:.2f}")
    except Exception as e:
        logging.error(f"移动页面失败: {str(e)}")
        raise


def generate_random(min_val: float, max_val: float) -> float:
    """
    生成指定范围内的随机数
    
    Args:
        min_val: 最小值
        max_val: 最大值
        
    Returns:
        float: 随机数
    """
    try:
        value = random.uniform(min_val, max_val)
        logging.info(f"生成随机数: {value:.3f} (范围: {min_val} - {max_val})")
        return value
    except Exception as e:
        logging.error(f"生成随机数失败: {str(e)}")
        raise


# 操作函数映射表
OPERATIONS = {
    'input': input_text,
    'move': move_page,
    'random': generate_random,
}


def evaluate_nested_operation(operation: str) -> Any:
    """
    解析并执行嵌套的操作
    
    Args:
        operation: 操作字符串，可能包含嵌套操作，如 "input(random(0.1,0.2))"
        
    Returns:
        Any: 操作结果
    """
    # 使用正则表达式查找最内层的函数调用
    pattern = r'(\w+)\(([\d\.,\s-]+)\)'
    match = re.search(pattern, operation)
    
    if not match:
        return operation.strip("'\"")  # 如果是普通字符串，直接返回
        
    func_name = match.group(1)
    args_str = match.group(2)
    args = [float(arg.strip()) for arg in args_str.split(',')]
    
    if func_name not in OPERATIONS:
        raise ValueError(f"未知的操作: {func_name}")
        
    # 执行操作
    result = OPERATIONS[func_name](*args)
    
    # 如果还有外层操作，替换结果并继续解析
    new_operation = operation.replace(match.group(0), str(result))
    if '(' in new_operation:
        return evaluate_nested_operation(new_operation)
        
    return result


def execute_operation(operation: str) -> None:
    """
    执行操作
    
    Args:
        operation: 操作字符串
    """
    try:
        # 分离操作名称和参数
        op_name = operation.split('(')[0].strip()
        args_str = operation[len(op_name):].strip('()')
        
        if op_name not in OPERATIONS:
            raise ValueError(f"未知的操作: {op_name}")
            
        # 如果是input操作，需要特殊处理嵌套操作
        if op_name == 'input':
            result = evaluate_nested_operation(args_str)
            OPERATIONS[op_name](result)
        else:
            # 解析参数
            args = []
            if args_str:
                # 处理字符串参数
                if args_str.startswith('"') or args_str.startswith("'"):
                    args = [args_str.strip("'\"")]
                else:
                    # 处理数值参数
                    args = [float(arg.strip()) for arg in args_str.split(',')]
            
            # 执行操作
            OPERATIONS[op_name](*args)
            
    except Exception as e:
        logging.error(f"执行操作失败: {operation}, 错误: {str(e)}")
        raise


def handle_operations(operations: Dict[str, Any]) -> None:
    """
    处理操作
    
    Args:
        operations: 操作字典
    """
    for op_name, args in operations.items():
        if op_name not in OPERATIONS:
            raise ValueError(f"未知的操作: {op_name}")
        
        # 执行操作
        OPERATIONS[op_name](*args)


# 示例使用
if __name__ == "__main__":
    operations = {
        'input': ['Hello, World!'],
        'move': [0.5, 0.5],
        'random': [0.1, 0.9]
    }
    handle_operations(operations)
