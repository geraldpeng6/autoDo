"""
配置模块
"""
import os


class Settings:
    """配置类"""
    
    def __init__(self):
        # 屏幕缩放比例
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # MetaMask配置
        self.metamask_password = os.getenv('METAMASK_PASSWORD', 'password')


# 全局配置实例
settings = Settings()
