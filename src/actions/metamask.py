"""
MetaMask操作模块
"""
import time
import logging
import pyautogui
import os

from src.image.template_matcher import find_template
from src.actions.mouse import click_position
from src.config import settings


def click_blue_button_for_metamask():
    """
    点击MetaMask的蓝色按钮
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
    处理MetaMask登录
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
        pyautogui.typewrite(settings.metamask_password)
        time.sleep(0.5)
        pyautogui.press('enter')
        
        return True
        
    except Exception as e:
        logging.error(f"处理MetaMask登录失败: {str(e)}")
        return False


def handle_metamask_extension():
    """
    处理MetaMask扩展
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
    处理MetaMask的整个流程，包括点击、连接、登录等
    
    Args:
        match_pos: 匹配位置
        template_size: 模板大小
        
    Returns:
        bool: 处理是否成功
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
        if find_template(['pics/pics_metamask/mima.png'])[0]:
            logging.info("检测到登录界面，处理登录")
            if handle_metamask_login():
                return True
            return False
        # 如果没有登录界面，可能需要先点击扩展
        if handle_metamask_extension():
            time.sleep(1)
            if click_blue_button_for_metamask() == 0:
                    # 再检查是否有登录界面
                if find_template(['pics/pics_metamask/mima.png'])[0]:
                    if not handle_metamask_login():
                        error_msg = "MetaMask登录失败"
                        logging.error(error_msg)
                        return False
            else:
                return True
    else:
        return True

    error_msg = "MetaMask处理失败"
    logging.error(error_msg)
    return False
