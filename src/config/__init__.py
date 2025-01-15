"""
配置模块
提供全局配置管理，包括屏幕缩放比例和MetaMask密码等设置。
"""
import os


class Settings:
    """
    配置类
    
    Attributes:
        scale_x (float): X轴屏幕缩放比例，默认为1.0
        scale_y (float): Y轴屏幕缩放比例，默认为1.0
        metamask_password (str): MetaMask钱包密码，从环境变量获取，默认为'password'
        
    Note:
        - 屏幕缩放比例用于坐标转换
        - MetaMask密码优先从环境变量METAMASK_PASSWORD获取
    """
    
    def __init__(self):
        # 屏幕缩放比例
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.display_width = 2560
        self.display_height = 1600
        # MetaMask配置
        self.metamask_password = os.getenv('METAMASK_PASSWORD', 'password')


# 全局配置实例
settings = Settings()
