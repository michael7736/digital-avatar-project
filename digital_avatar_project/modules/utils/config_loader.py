#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置加载工具
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器，用于加载和管理配置文件"""
    
    def __init__(self, config_path):
        """初始化配置加载器
        
        Args:
            config_path (str): 配置文件路径
        """
        self.config_path = config_path
        self.config = {}
        
    def load(self):
        """加载配置文件
        
        Returns:
            dict: 配置字典
        """
        logger.info(f"加载配置文件: {self.config_path}")
        
        try:
            # 检查文件是否存在
            if not Path(self.config_path).exists():
                logger.warning(f"配置文件不存在: {self.config_path}, 将使用默认配置")
                return self._load_default_config()
            
            # 加载配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # 验证配置
            self._validate_config()
            
            return self.config
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            logger.info("将使用默认配置")
            return self._load_default_config()
    
    def _validate_config(self):
        """验证配置是否包含所需的键"""
        required_keys = [
            "voice_synthesis",
            "face_animation",
            "lip_sync",
            "chatbot",
            "streaming"
        ]
        
        for key in required_keys:
            if key not in self.config:
                logger.warning(f"配置中缺少键: {key}")
                self.config[key] = {}
    
    def _load_default_config(self):
        """加载默认配置
        
        Returns:
            dict: 默认配置字典
        """
        default_config = {
            "voice_synthesis": {
                "engine": "openai",
                "voice": "alloy",
                "language": "zh-CN",
                "pitch": 1.0,
                "rate": 1.0,
                "volume": 1.0
            },
            "face_animation": {
                "model": "3d",
                "avatar_path": "assets/avatars/default.png",
                "animations_enabled": True
            },
            "lip_sync": {
                "engine": "wav2lip",
                "smooth_factor": 0.5,
                "frame_rate": 30
            },
            "chatbot": {
                "engine": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 150,
                "system_prompt": "你是一个友好的数字人助手。"
            },
            "streaming": {
                "enable": True,
                "platform": "rtmp",
                "url": "rtmp://localhost/live",
                "key": "stream",
                "video_bitrate": "2500k",
                "audio_bitrate": "128k",
                "resolution": "720p"
            }
        }
        
        # 创建默认配置文件
        os.makedirs(Path(self.config_path).parent, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        logger.info(f"已创建默认配置文件: {self.config_path}")
        
        return default_config 