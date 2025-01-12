import cv2
import numpy as np
import pyautogui
import time
import os
import random
import logging
from datetime import datetime

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = './logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'auto_do_{timestamp}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return log_file

def get_screen_info():
    """获取屏幕信息和缩放比例"""
    try:
        screen_width, screen_height = pyautogui.size()
        screenshot = pyautogui.screenshot()
        screenshot_width, screenshot_height = screenshot.size
        
        scale_x = screen_width / screenshot_width
        scale_y = screen_height / screenshot_height
        
        logging.info(f"屏幕分辨率: {screen_width}x{screen_height}")
        logging.info(f"截图大小: {screenshot_width}x{screenshot_height}")
        logging.info(f"缩放比例 - X轴: {scale_x}, Y轴: {scale_y}")
        
        return scale_x, scale_y
    except Exception as e:
        error_msg = f"获取屏幕信息出错: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)

def find_template(template_file, scale_x, scale_y, max_wait_time=10, check_interval=0.5):
    """
    查找模板图片位置，支持多尺度匹配
    """
    template_path = os.path.join('./pics', template_file)
    
    # 读取模板图像
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        error_msg = f"无法读取模板图像: {template_path}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
    
    # 转换为灰度图
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = template_gray.shape[::-1]
    
    # 创建不同尺度的模板
    scales = [0.8, 0.9, 1.0, 1.1, 1.2]  # 尝试不同的缩放比例
    templates = []
    for scale in scales:
        width = int(w * scale)
        height = int(h * scale)
        if width > 0 and height > 0:
            resized = cv2.resize(template_gray, (width, height), interpolation=cv2.INTER_AREA)
            # 对调整后的模板进行轻微的高斯模糊，增加匹配容忍度
            blurred = cv2.GaussianBlur(resized, (3, 3), 0)
            templates.append((blurred, scale, width, height))
    
    start_time = time.time()
    attempt = 1
    best_match = None
    best_scale = 1.0
    best_val = 0
    
    while True:
        # 获取新的屏幕截图
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        # 对截图也进行轻微的高斯模糊
        screenshot_gray = cv2.GaussianBlur(screenshot_gray, (3, 3), 0)
        
        # 在不同尺度下进行模板匹配
        for template_scaled, scale, width, height in templates:
            # 使用归一化相关系数方法进行模板匹配
            res = cv2.matchTemplate(screenshot_gray, template_scaled, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            # 更新最佳匹配
            if max_val > best_val:
                best_val = max_val
                best_match = max_loc
                best_scale = scale
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # 如果找到足够好的匹配
        if best_val > 0.8:
            logging.info(f"在第 {attempt} 次尝试中找到匹配（用时 {elapsed_time:.1f} 秒）: {template_file}")
            logging.info(f"最佳匹配比例: {best_scale:.2f}, 匹配度: {best_val:.2f}")
            
            # 根据最佳缩放比例调整返回的位置和大小
            final_w = int(w * best_scale)
            final_h = int(h * best_scale)
            
            # 保存调试图片
            save_debug_image(screenshot, [(best_match[0], best_match[1])], template_file, 
                           final_w, final_h, scale_x, scale_y, best_scale, best_val)
            
            return best_match, (final_w, final_h)
        
        if elapsed_time >= max_wait_time:
            error_msg = f"在 {max_wait_time} 秒内未找到匹配 {template_file}，共尝试 {attempt} 次"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        
        # logging.info(f"第 {attempt} 次尝试未找到匹配 {template_file}，{max_wait_time - elapsed_time:.1f} 秒后重试...")
        attempt += 1
        time.sleep(check_interval)

def save_debug_image(screenshot, matches, template_file, w, h, scale_x, scale_y, match_scale=1.0, match_value=0):
    """
    保存调试图片，显示模板匹配位置
    Args:
        match_scale: 最佳匹配的缩放比例
        match_value: 匹配度值
    """
    try:
        debug_img = screenshot.copy()
        
        for (x, y) in matches:
            # 在原始位置画一个绿色矩形
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 在中心位置画一个红色点
            center_x = x + w // 2
            center_y = y + h // 2
            cv2.circle(debug_img, (center_x, center_y), 5, (0, 0, 255), -1)
            
            # 添加匹配信息
            info_text = f"Scale: {match_scale:.2f}, Confidence: {match_value:.2f}"
            cv2.putText(debug_img, info_text, (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # 添加坐标文本
            text = f"Original: ({x}, {y})"
            cv2.putText(debug_img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # 计算实际点击位置
            click_x = int(x + w/2)
            click_y = int(y + h/2)
            text = f"Click: ({click_x}, {click_y})"
            cv2.putText(debug_img, text, (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # 保存图片
        os.makedirs('debugForTu', exist_ok=True)
        debug_path = os.path.join('debugForTu', f'debug_{template_file}')
        cv2.imwrite(debug_path, debug_img)
        logging.info(f"已保存debug图片: {debug_path}")
        
    except Exception as e:
        logging.error(f"保存debug图片时出错: {str(e)}")

def click_position(match_pos, template_size, scale_x, scale_y, offset_x=0, offset_y=0):
    """
    点击指定位置，支持位置偏移
    
    Args:
        match_pos: 匹配位置的坐标
        template_size: 模板图片的尺寸 (width, height)
        scale_x: X轴缩放比例
        scale_y: Y轴缩放比例
        offset_x: X轴偏移量，正值向右偏移，负值向左偏移，范围-1到1，表示偏移模板宽度的比例
        offset_y: Y轴偏移量，正值向下偏移，负值向上偏移，范围-1到1，表示偏移模板高度的比例
    """
    if match_pos is None:
        return False
    
    w, h = template_size
    
    # 计算中心位置
    center_x = int((match_pos[0] + w / 2) * scale_x)
    center_y = int((match_pos[1] + h / 2) * scale_y)
    
    # 计算偏移后的位置
    offset_pixel_x = int(w * scale_x * offset_x)  # 将比例转换为像素偏移
    offset_pixel_y = int(h * scale_y * offset_y)
    
    final_x = center_x + offset_pixel_x
    final_y = center_y + offset_pixel_y
    
    logging.info(f"原始中心位置: ({center_x}, {center_y})")
    logging.info(f"偏移量: X={offset_pixel_x}, Y={offset_pixel_y}")
    logging.info(f"最终点击位置: ({final_x}, {final_y})")
    
    pyautogui.moveTo(final_x, final_y, duration=0.1)
    pyautogui.click()
    return True

def get_input_text(input_name):
    """根据输入框名称返回对应的文本"""
    try:
        input_number = int(''.join(filter(str.isdigit, input_name)))
    except ValueError:
        error_msg = f"无法从{input_name}提取输入框序号"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    if input_number == 1:
        random_number = round(random.uniform(0.1, 0.2), 3)
        text = str(random_number)
        logging.info(f"生成随机数: {text}")
        return text
    else:
        text = f"输入框{input_number}的文本"
        logging.info(f"使用默认文本: {text}")
        return text

def type_text(text):
    """输入文本"""
    if text is None:
        return
    pyautogui.typewrite(text, interval=0.5)
    logging.info(f"已输入文本: {text}")

def check_balance_status():
    """检查是否出现余额不足提示"""
    try:
        # 尝试查找余额不足的图片
        match_pos, _ = find_template('balanceNotAvailable.png', scale_x, scale_y, max_wait_time=2, check_interval=0.5)
        if match_pos:
            logging.warning("检测到余额不足提示")
            return True
        return False
    except Exception:
        return False

def check_image_exists(image_name, wait_time=2):
    """检查图片是否存在"""
    try:
        match_pos, _ = find_template(image_name, scale_x, scale_y, max_wait_time=wait_time, check_interval=0.5)
        return match_pos is not None
    except Exception:
        return False

def handle_metamask_login():
    """处理MetaMask登录流程"""
    try:
        # 检查是否出现密码输入框
        match_pos, template_size = find_template('mima.png', scale_x, scale_y, max_wait_time=3, check_interval=0.5)
        if match_pos:
            logging.info("检测到MetaMask登录界面")
            
            # 点击密码输入框
            if not click_position(match_pos, template_size, scale_x, scale_y):
                logging.error("无法点击密码输入框")
                return False
            
            # 输入密码
            time.sleep(0.5)
            type_text("password")
            logging.info("已输入密码")
            
            # 查找并点击登录按钮
            time.sleep(0.5)
            login_pos, login_size = find_template('loginButton.png', scale_x, scale_y, max_wait_time=3, check_interval=0.5)
            if not login_pos or not click_position(login_pos, login_size, scale_x, scale_y):
                logging.error("无法找到或点击登录按钮")
                return False
            
            logging.info("完成MetaMask登录")
            return True
    except Exception as e:
        logging.error(f"处理MetaMask登录时出错: {str(e)}")
        return False
    
    return False

def handle_metamask_extension():
    """处理MetaMask扩展图标点击"""
    try:
        # 检查是否存在扩展图标
        match_pos, template_size = find_template('kuozhan.png', scale_x, scale_y, max_wait_time=3, check_interval=0.5)
        if match_pos:
            logging.info("检测到MetaMask扩展图标")
            if click_position(match_pos, template_size, scale_x, scale_y):
                logging.info("已点击MetaMask扩展图标")
                return True
            else:
                logging.error("无法点击MetaMask扩展图标")
                return False
    except Exception as e:
        logging.error(f"处理MetaMask扩展图标时出错: {str(e)}")
        return False
    return False

def scroll_down(scroll_amount=100):
    """
    在浏览器中向下滚动
    Args:
        scroll_amount: 滚动的像素量，正数向下滚动，负数向上滚动
    """
    try:
        pyautogui.scroll(-scroll_amount)  # pyautogui中负数表示向下滚动
        logging.info(f"向下滚动 {scroll_amount} 像素")
    except Exception as e:
        logging.error(f"滚动操作失败: {str(e)}")

def select_and_delete():
    """全选并删除文本"""
    try:
        time.sleep(0.1)
        # 在Mac上使用Command+A全选
        pyautogui.hotkey('command', 'a')
        time.sleep(0.1)
        # 按删除键
        pyautogui.press('delete')
        logging.info("已执行全选并删除操作")
    except Exception as e:
        logging.error(f"全选删除操作失败: {str(e)}")

def main():
    try:
        # 设置日志
        log_file = setup_logging()
        logging.info("程序开始运行")
        logging.info(f"日志文件位置: {log_file}")
        
        # 等待用户准备
        logging.info("程序将在5秒后开始运行...")
        time.sleep(5)
        
        # 获取屏幕信息
        global scale_x, scale_y
        scale_x, scale_y = get_screen_info()
        
        # 读取templates.txt文件获取图片列表
        with open('templates.txt', 'r') as f:
            template_files = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        logging.info(f"将按顺序匹配以下图片: {template_files}")
        
        # 处理每个模板图片
        i = 0
        while i < len(template_files):
            template_file = template_files[i]
            logging.info(f"\n开始处理图片: {template_file}")
            
            # 查找并点击图片
            match_pos, template_size = find_template(template_file, scale_x, scale_y)
            
            # 特殊处理MetaMask登录情况
            if template_file == '2MetaMask.png':
                if match_pos and click_position(match_pos, template_size, scale_x, scale_y):
                    # 点击成功后，先等待一下看是否需要登录
                    time.sleep(0.1)
                    
                    # 先检查是否有连接界面
                    if check_image_exists('3lianjie.png'):
                        logging.info("检测到连接界面，继续后续操作")
                        i += 1
                        continue
                    
                    # 如果没有连接界面，检查是否需要登录
                    if check_image_exists('mima.png'):
                        logging.info("检测到登录界面，处理登录")
                        if handle_metamask_login():
                            time.sleep(2)  # 登录成功后等待页面加载
                        else:
                            error_msg = "MetaMask登录失败"
                            logging.error(error_msg)
                            raise RuntimeError(error_msg)
                    else:
                        # 如果既没有连接界面也没有登录界面，尝试点击扩展图标
                        logging.info("未检测到连接界面或登录界面，尝试点击扩展图标")
                        if handle_metamask_extension():
                            time.sleep(1)
                            # 再次检查是否需要处理登录
                            if check_image_exists('mima.png'):
                                if not handle_metamask_login():
                                    error_msg = "MetaMask登录失败"
                                    logging.error(error_msg)
                                    raise RuntimeError(error_msg)
                                time.sleep(2)
                    
                    # 继续执行下一个图片的处理
                    i += 1
                    continue
                else:
                    error_msg = f"无法找到或点击图片: {template_file}"
                    logging.error(error_msg)
                    raise RuntimeError(error_msg)
            
            # 对于input开头的图片，点击位置向左偏移40%
            if template_file.startswith('input'):
                if not match_pos or not click_position(match_pos, template_size, scale_x, scale_y, offset_x=-0.4):
                    error_msg = f"无法找到或点击图片: {template_file}"
                    logging.error(error_msg)
                    raise RuntimeError(error_msg)
                
                # 特殊处理input1
                if template_file == 'input1.png':
                    # 先全选删除
                    time.sleep(0.2)  # 等待输入框准备好
                    select_and_delete()
                    time.sleep(0.2)  # 等待删除完成
                    
                    # 输入文本
                    input_text = get_input_text(template_file)
                    type_text(input_text)
                    
                    # 输入后向下滚动
                    time.sleep(0.2)  # 等待输入完成
                    scroll_down(150)  # 向下滚动150像素
                    time.sleep(0.5)  # 等待滚动完成
                    
                    # 检查余额
                    if check_balance_status():
                        error_msg = "余额不足，程序终止"
                        logging.error(error_msg)
                        raise RuntimeError(error_msg)
                else:
                    # 其他input直接输入文本
                    input_text = get_input_text(template_file)
                    type_text(input_text)
            else:
                # 普通图片点击中心位置
                if not match_pos or not click_position(match_pos, template_size, scale_x, scale_y):
                    error_msg = f"无法找到或点击图片: {template_file}"
                    logging.error(error_msg)
                    raise RuntimeError(error_msg)
            
            i += 1
        
        logging.info("程序成功完成所有操作")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
