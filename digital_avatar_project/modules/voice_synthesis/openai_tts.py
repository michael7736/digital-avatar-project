#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import tempfile
from typing import Optional, Dict, Any

import openai
from openai import OpenAI

from .interface import VoiceSynthesizer


class OpenAITTS(VoiceSynthesizer):
    """使用OpenAI TTS API的语音合成器实现"""
    
    def __init__(self):
        self.logger = logging.getLogger("OpenAITTS")
        self.client = None
        self.config = {}
        self.available_voices = {
            "alloy": {"name": "Alloy", "gender": "neutral", "description": "平和中性的声音"},
            "echo": {"name": "Echo", "gender": "male", "description": "低沉和深邃的声音"},
            "fable": {"name": "Fable", "gender": "female", "description": "温暖和柔和的声音"},
            "onyx": {"name": "Onyx", "gender": "male", "description": "权威和清晰的声音"},
            "nova": {"name": "Nova", "gender": "female", "description": "友好和对话的声音"},
            "shimmer": {"name": "Shimmer", "gender": "female", "description": "轻快和积极的声音"},
        }
        
        # OpenAI TTS不支持情感控制
        self.emotions = {}
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化OpenAI TTS客户端
        
        Args:
            config: 配置参数，必须包含api_key
            
        Returns:
            初始化是否成功
        """
        try:
            if 'api_key' not in config:
                self.logger.error("配置中缺少OpenAI API密钥")
                return False
            
            self.config = config
            
            # 初始化OpenAI客户端
            self.client = OpenAI(api_key=config['api_key'])
            
            # 设置API基础URL（如果有提供）
            if 'api_base' in config:
                openai.api_base = config['api_base']
            
            # 测试API连接
            self._test_connection()
            
            self.logger.info("OpenAI TTS 初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化OpenAI TTS时出错: {str(e)}")
            return False
    
    def _test_connection(self) -> None:
        """测试API连接"""
        try:
            # 创建一个非常短的音频以测试连接
            self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input="测试"
            )
            self.logger.info("API连接测试成功")
        except Exception as e:
            self.logger.error(f"API连接测试失败: {str(e)}")
            raise
    
    def synthesize(self, text: str, output_path: str, voice_id: Optional[str] = None, 
                  emotion: Optional[str] = None, speed: float = 1.0) -> str:
        """
        将文本合成为语音
        
        Args:
            text: 待合成的文本
            output_path: 输出文件路径
            voice_id: 声音ID，默认为alloy
            emotion: 情感类型（OpenAI TTS不支持）
            speed: 语速（OpenAI TTS不支持直接控制语速）
            
        Returns:
            生成的音频文件路径
        """
        if not self.client:
            raise RuntimeError("OpenAI TTS 尚未初始化")
        
        try:
            # 使用默认声音如果未指定
            if not voice_id or voice_id not in self.available_voices:
                voice_id = "alloy"
                self.logger.warning(f"使用默认声音: {voice_id}")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # 调用OpenAI API
            response = self.client.audio.speech.create(
                model="tts-1",  # 也可以使用tts-1-hd获得更高质量
                voice=voice_id,
                input=text
            )
            
            # 保存音频文件
            response.stream_to_file(output_path)
            
            self.logger.info(f"语音合成成功: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"语音合成失败: {str(e)}")
            raise
    
    def clone_voice(self, audio_path: str, voice_name: str) -> str:
        """
        从音频样本克隆声音 (OpenAI目前不支持公开API，使用旁路解决方案)
        
        Args:
            audio_path: 音频样本路径
            voice_name: 声音名称
            
        Returns:
            生成的声音ID
        """
        self.logger.warning("OpenAI TTS当前不支持通过API进行声音克隆")
        return ""
    
    def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        获取可用的声音列表
        
        Returns:
            声音ID到声音信息的映射
        """
        return self.available_voices
    
    def get_emotions(self) -> Dict[str, str]:
        """
        获取支持的情感类型
        
        Returns:
            情感ID到情感描述的映射 (OpenAI TTS不支持)
        """
        return self.emotions 