"""
MetaMask操作模块
提供MetaMask钱包相关的自动化操作，包括登录、扩展管理等功能。
"""
import time
import logging
import pyautogui
import os

from src.image.template_matcher import find_template
from src.actions.mouse import click_position
from src.config import settings
from src.actions.operations import input_text


def click_blue_button_for_metamask():
    """
    点击MetaMask的蓝色按钮
    
    Returns:
        int: 成功点击的次数
        
    Note:
        - 最多尝试3秒，每0.5秒检查一次
        - 如果找不到按钮会按ESC键
        - 每次点击后会等待0.3秒
    """
    count = 0
    while True:
        match_pos, template_size = find_template(['pics/pics_metamask/blueButton.png'],
                                                 max_wait_time=3, check_interval=0.5)
        if match_pos:
            logging.info("检测到MetaMask的蓝色按钮")
            if not click_position(match_pos, template_size,
                                 settings.scale_x,
                                 settings.scale_y):
                return count
            count += 1
            time.sleep(0.3)
        else:
            pyautogui.press('esc')
            if count == 0:  # 如果一次都没找到按钮
                logging.info("未找到MetaMask蓝色按钮")
            return count


def handle_metamask_login():
    """
    处理MetaMask登录流程
    
    Returns:
        bool: 登录是否成功
        
    Note:
        - 会自动检测登录界面
        - 使用配置文件中的密码
        - 登录后会自动处理可能出现的蓝色按钮
    """
    try:
        # 检测是否在登录界面
        match_pos, template_size = find_template(['pics/pics_metamask/mima.png'])
        if not match_pos:
            return False
            
        logging.info("检测到登录界面，处理登录")
        
        # 点击密码输入框
        if not match_pos or not click_position(match_pos, template_size,
                                             settings.scale_x,
                                             settings.scale_y):
            error_msg = "无法找到或点击密码输入框"
            logging.error(error_msg)
            return False
            
        time.sleep(0.5)
        
        # 输入密码并按回车
        input_text(settings.metamask_password)
        time.sleep(0.5)
        pyautogui.press('enter')
        click_blue_button_for_metamask()
        return True
        
    except Exception as e:
        logging.error(f"处理MetaMask登录失败: {str(e)}")
        return False


def handle_metamask_extension():
    """
    处理MetaMask浏览器扩展
    
    Returns:
        bool: 处理是否成功
        
    Note:
        - 会尝试查找并点击MetaMask扩展图标
        - 失败时会记录错误日志
    """
    try:
        match_pos, template_size = find_template(['pics/pics_metamask/extension.png'])
        if not match_pos or not click_position(match_pos, template_size,
                                             settings.scale_x,
                                             settings.scale_y):
            error_msg = "无法找到或点击MetaMask扩展"
            logging.error(error_msg)
            return False
            
        return True
        
    except Exception as e:
        logging.error(f"处理MetaMask扩展失败: {str(e)}")
        return False


def handle_metamask_process(match_pos, template_size):
    """
    处理MetaMask的完整流程
    
    Args:
        match_pos (tuple): 匹配到的位置坐标 (x, y)
        template_size (tuple): 模板图片大小 (width, height)
        
    Returns:
        bool: 处理是否成功
        
    Note:
        - 包括点击、连接、登录等完整流程
        - 出错时会记录详细的错误信息
    """
    # 先检查并点击MetaMask网页
    if not match_pos or not click_position(match_pos, template_size,
                                         settings.scale_x,
                                         settings.scale_y):
        error_msg = "无法找到或点击MetaMask网页相关元素"
        logging.error(error_msg)
        return False
        
    time.sleep(0.1)

    # 如果没有连接界面，检查是否需要登录
    if click_blue_button_for_metamask() == 0:
        if handle_metamask_login():
            return True
        if handle_metamask_extension():
            if handle_metamask_login():
                return True
            else:
                click_blue_button_for_metamask()
                return True
    else:
        return True

    error_msg = "MetaMask它处理失败"
    logging.error(error_msg)
    return False
