#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数字人直播系统主程序
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
import tempfile

import cv2
import numpy as np

# 添加项目根目录到路径
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# 导入模块
from modules.voice_synthesis.tts_manager import TTSManager
from modules.face_animation.image_avatar import ImageAvatar
from modules.lip_sync.sad_talker import SadTalker
from modules.chatbot.openai_chatbot import OpenAIChatbot
from modules.streaming.rtmp_streamer import RTMPStreamer
from modules.streaming.virtual_camera import VirtualCamera

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('digital_avatar.log', mode='a')
    ]
)

logger = logging.getLogger("DigitalAvatarSystem")


class DigitalAvatarSystem:
    """数字人直播系统主类"""
    
    def __init__(self, config_path=None):
        """
        初始化系统
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="digital_avatar_"))
        self.logger.info(f"临时目录: {self.temp_dir}")
        
        # 确保临时目录存在
        os.makedirs(self.temp_dir / "audio", exist_ok=True)
        os.makedirs(self.temp_dir / "video", exist_ok=True)
        
        # 初始化各模块
        self.tts = None
        self.avatar = None
        self.lip_syncer = None
        self.chatbot = None
        self.streamer = None
        
        # 实时状态
        self.running = False
        self.current_audio = None
        self.current_video = None
        
    def _load_config(self, config_path):
        """加载配置文件"""
        if not config_path:
            config_path = Path(current_dir) / "configs" / "default.json"
        
        if not os.path.exists(config_path):
            self.logger.error(f"配置文件不存在: {config_path}")
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info(f"已加载配置文件: {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件出错: {str(e)}")
            raise
    
    def initialize(self):
        """初始化所有模块"""
        self.logger.info("开始初始化模块...")
        
        # 初始化语音合成
        self._init_tts()
        
        # 初始化虚拟形象
        self._init_avatar()
        
        # 初始化唇语同步
        self._init_lip_sync()
        
        # 初始化对话系统
        self._init_chatbot()
        
        # 初始化直播推流
        self._init_streamer()
        
        self.logger.info("所有模块初始化完成")
        return True
    
    def _init_tts(self):
        """初始化语音合成模块"""
        try:
            tts_config = self.config.get("voice_synthesis", {})
            self.tts = TTSManager(tts_config)
            self.logger.info(f"语音合成模块初始化成功，引擎: {tts_config.get('engine', 'openai')}")
        except Exception as e:
            self.logger.error(f"初始化语音合成模块失败: {str(e)}")
            raise
    
    def _init_avatar(self):
        """初始化虚拟形象模块"""
        try:
            avatar_config = self.config.get("face_animation", {})
            self.avatar = ImageAvatar()
            if not self.avatar.initialize(avatar_config):
                raise RuntimeError("虚拟形象初始化失败")
            
            # 加载默认形象
            avatar_path = avatar_config.get("avatar_path")
            if avatar_path:
                if not self.avatar.load_avatar(avatar_path):
                    self.logger.warning(f"无法加载默认虚拟形象: {avatar_path}")
            
            self.logger.info("虚拟形象模块初始化成功")
        except Exception as e:
            self.logger.error(f"初始化虚拟形象模块失败: {str(e)}")
            raise
    
    def _init_lip_sync(self):
        """初始化唇语同步模块"""
        try:
            lip_sync_config = self.config.get("lip_sync", {})
            self.lip_syncer = SadTalker()
            if not self.lip_syncer.initialize(lip_sync_config):
                raise RuntimeError("唇语同步初始化失败")
            
            self.logger.info("唇语同步模块初始化成功")
        except Exception as e:
            self.logger.error(f"初始化唇语同步模块失败: {str(e)}")
            raise
    
    def _init_chatbot(self):
        """初始化对话管理模块"""
        try:
            chatbot_config = self.config.get("chatbot", {})
            self.chatbot = OpenAIChatbot()
            if not self.chatbot.initialize(chatbot_config):
                raise RuntimeError("对话系统初始化失败")
            
            self.logger.info("对话管理模块初始化成功")
        except Exception as e:
            self.logger.error(f"初始化对话管理模块失败: {str(e)}")
            raise
    
    def _init_streamer(self):
        """初始化直播推流模块"""
        try:
            streaming_config = self.config.get("streaming", {})
            platform = streaming_config.get("platform", "rtmp")
            
            if platform == "rtmp":
                self.streamer = RTMPStreamer()
            elif platform == "virtual_camera":
                self.streamer = VirtualCamera()
            else:
                self.logger.error(f"不支持的直播平台: {platform}")
                raise ValueError(f"不支持的直播平台: {platform}")
            
            if not self.streamer.initialize(streaming_config):
                raise RuntimeError("直播推流初始化失败")
            
            self.logger.info(f"直播推流模块初始化成功，平台: {platform}")
        except Exception as e:
            self.logger.error(f"初始化直播推流模块失败: {str(e)}")
            raise
    
    def process_text(self, text, output_prefix=None):
        """
        处理文本：生成语音 -> 生成唇语同步视频 -> 输出
        
        Args:
            text: 要处理的文本
            output_prefix: 输出文件前缀
            
        Returns:
            (audio_path, video_path): 生成的音频和视频文件路径
        """
        try:
            # 生成唯一文件前缀
            timestamp = int(time.time())
            if not output_prefix:
                output_prefix = f"output_{timestamp}"
            
            # 合成语音
            audio_path = self.temp_dir / "audio" / f"{output_prefix}.mp3"
            audio_path = self.tts.synthesize(text, str(audio_path))
            self.logger.info(f"语音合成完成: {audio_path}")
            
            # 获取虚拟形象信息
            avatar_info = self.avatar.get_avatar_info()
            if not avatar_info:
                raise ValueError("没有加载虚拟形象")
            
            # 唇语同步
            video_path = self.temp_dir / "video" / f"{output_prefix}.mp4"
            video_path = self.lip_syncer.synchronize(
                audio_path=audio_path,
                image_path=avatar_info["path"],
                output_path=str(video_path)
            )
            self.logger.info(f"唇语同步完成: {video_path}")
            
            # 更新当前音视频
            self.current_audio = audio_path
            self.current_video = video_path
            
            return audio_path, video_path
            
        except Exception as e:
            self.logger.error(f"处理文本时出错: {str(e)}")
            raise
    
    def stream_video(self, video_path):
        """
        流式输出视频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            是否成功输出
        """
        if not self.streamer:
            self.logger.error("直播推流模块未初始化")
            return False
        
        try:
            # 开始推流（如果尚未开始）
            if not self.streamer.is_streaming():
                if not self.streamer.start_streaming():
                    self.logger.error("开始直播失败")
                    return False
            
            # 发送视频
            if not self.streamer.send_video(video_path):
                self.logger.error(f"发送视频失败: {video_path}")
                return False
            
            self.logger.info(f"视频正在推流: {video_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"推流视频时出错: {str(e)}")
            return False
    
    def process_user_input(self, user_input):
        """
        处理用户输入
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            生成的视频路径
        """
        try:
            # 获取对话回复
            response = self.chatbot.get_response(user_input)
            self.logger.info(f"用户: {user_input} -> 助手: {response}")
            
            # 处理响应文本
            _, video_path = self.process_text(response)
            
            # 推流视频
            self.stream_video(video_path)
            
            return video_path
            
        except Exception as e:
            self.logger.error(f"处理用户输入时出错: {str(e)}")
            raise
    
    def simulate_conversation(self):
        """模拟对话"""
        self.logger.info("开始模拟对话...")
        
        # 获取模拟输入
        simulated_inputs = self.config.get("chatbot", {}).get("simulated_inputs", [])
        if not simulated_inputs:
            simulated_inputs = [
                "你好，请自我介绍一下",
                "今天天气真不错",
                "你能做什么？",
                "讲个笑话吧"
            ]
        
        for user_input in simulated_inputs:
            self.logger.info(f"模拟用户输入: {user_input}")
            video_path = self.process_user_input(user_input)
            # 等待视频播放完成
            time.sleep(2)
        
        self.logger.info("模拟对话结束")
    
    def run(self):
        """运行系统"""
        try:
            self.logger.info("系统启动...")
            self.running = True
            
            # 初始化模块
            self.initialize()
            
            # 模拟对话
            self.simulate_conversation()
            
            # 等待用户退出信号
            self.logger.info("系统正在运行，按Ctrl+C退出")
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("接收到退出信号")
        except Exception as e:
            self.logger.error(f"系统运行时出错: {str(e)}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("开始清理资源...")
        
        # 清理各模块
        if self.streamer:
            self.streamer.cleanup()
        
        if self.lip_syncer:
            self.lip_syncer.cleanup()
        
        if self.avatar:
            self.avatar.cleanup()
        
        # 清理临时文件
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"已删除临时目录: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"清理临时文件时出错: {str(e)}")
        
        self.running = False
        self.logger.info("系统已关闭")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="数字人直播系统")
    parser.add_argument("--config", "-c", type=str, 
                        help="配置文件路径")
    parser.add_argument("--debug", "-d", action="store_true", 
                        help="启用调试模式")
    parser.add_argument("--no-stream", "-n", action="store_true", 
                        help="不启动直播推流")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("调试模式已启用")
    
    # 创建系统实例
    system = DigitalAvatarSystem(args.config)
    
    # 运行系统
    system.run() 