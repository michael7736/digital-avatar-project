#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数字人直播系统测试脚本
"""

import os
import sys
import logging
import time
from pathlib import Path

# 添加项目根目录到sys.path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.append(str(PROJECT_ROOT))

# 导入各模块
from modules.voice_synthesis.tts_manager import TTSManager
from modules.face_animation.avatar_manager import AvatarManager
from modules.lip_sync.lip_sync_manager import LipSyncManager
from modules.chatbot.chatbot_manager import ChatbotManager
from modules.utils.config_loader import ConfigLoader

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    logger.info("开始测试数字人直播系统...")
    
    # 加载配置
    config_path = "configs/default.json"
    config = ConfigLoader(config_path).load()
    
    # 确保资源目录存在
    os.makedirs("assets/avatars", exist_ok=True)
    os.makedirs("temp/audio", exist_ok=True)
    os.makedirs("temp/videos", exist_ok=True)
    
    # 如果没有默认头像，创建一个空白图像
    if not Path("assets/avatars/default.png").exists():
        try:
            import numpy as np
            import cv2
            # 创建一个512x512的空白RGB图像
            img = np.ones((512, 512, 3), dtype=np.uint8) * 255
            # 画一个简单的人脸轮廓
            cv2.circle(img, (256, 256), 150, (200, 200, 200), -1)  # 面部
            cv2.circle(img, (200, 200), 30, (255, 255, 255), -1)   # 左眼
            cv2.circle(img, (312, 200), 30, (255, 255, 255), -1)   # 右眼
            cv2.ellipse(img, (256, 300), (80, 30), 0, 0, 180, (100, 100, 100), -1)  # 嘴巴
            # 保存图像
            os.makedirs("assets/avatars", exist_ok=True)
            cv2.imwrite("assets/avatars/default.png", img)
            logger.info("已创建默认头像")
        except ImportError:
            logger.warning("未安装opencv-python，无法创建默认头像")
    
    # 初始化对话管理器
    chatbot_manager = ChatbotManager(config["chatbot"])
    
    # 初始化语音合成管理器
    tts_manager = TTSManager(config["voice_synthesis"])
    
    # 初始化虚拟形象管理器
    avatar_manager = AvatarManager(config["face_animation"])
    
    # 初始化唇语同步管理器
    lip_sync_manager = LipSyncManager(config["lip_sync"])
    
    try:
        # 生成回复文本
        text = chatbot_manager.generate_response("你好，请简单介绍一下你自己")
        logger.info(f"生成的回复: {text}")
        
        # 语音合成
        audio_file = tts_manager.synthesize(text)
        logger.info(f"生成的音频文件: {audio_file}")
        
        if audio_file and Path(audio_file).exists():
            # 获取头像图像
            avatar_image = avatar_manager.get_avatar_image()
            logger.info(f"获取到头像图像, 形状: {avatar_image.shape}")
            
            # 唇语同步
            video_file = lip_sync_manager.generate(avatar_image, audio_file)
            logger.info(f"生成的视频文件: {video_file}")
            
            if video_file and Path(video_file).exists():
                logger.info(f"测试成功! 视频文件: {video_file}")
                return True
            else:
                logger.error("生成视频失败")
                return False
        else:
            logger.error("生成音频失败")
            return False
    
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    main() 