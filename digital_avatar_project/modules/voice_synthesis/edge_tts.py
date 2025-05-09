#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List

import edge_tts

from .interface import VoiceSynthesizer


class EdgeTTS(VoiceSynthesizer):
    """使用Microsoft Edge TTS的语音合成器实现"""
    
    def __init__(self):
        self.logger = logging.getLogger("EdgeTTS")
        self.config = {}
        self.available_voices = {}
        self.emotions = {
            "normal": "普通",
            "cheerful": "愉快",
            "sad": "悲伤",
            "angry": "愤怒",
            "afraid": "恐惧",
            "embarrassed": "尴尬",
            "serious": "严肃"
        }
        
        # 预加载声音列表
        self._preload_voices()
    
    async def _load_voices(self):
        """异步加载可用的声音列表"""
        try:
            voices = await edge_tts.list_voices()
            for voice in voices:
                voice_id = voice["ShortName"]
                gender = "female" if voice["Gender"] == "Female" else "male"
                locale = voice["Locale"]
                name = voice["DisplayName"]
                
                self.available_voices[voice_id] = {
                    "name": name,
                    "gender": gender,
                    "locale": locale,
                    "description": f"{name} ({locale})"
                }
                
            self.logger.info(f"已加载 {len(self.available_voices)} 个Edge TTS声音")
        except Exception as e:
            self.logger.error(f"加载Edge TTS声音列表失败: {str(e)}")
    
    def _preload_voices(self):
        """预加载声音列表"""
        asyncio.run(self._load_voices())
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化Edge TTS
        
        Args:
            config: 配置参数
            
        Returns:
            初始化是否成功
        """
        try:
            self.config = config
            
            # Edge TTS不需要API密钥，但是这里可以设置其他配置项
            self.logger.info("Edge TTS 初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化Edge TTS时出错: {str(e)}")
            return False
    
    async def _synthesize_async(self, text: str, output_path: str, voice_id: str, 
                               rate: str = "+0%", volume: str = "+0%") -> str:
        """
        异步合成语音
        
        Args:
            text: 待合成的文本
            output_path: 输出文件路径
            voice_id: 声音ID
            rate: 语速调整，如"+10%", "-5%"
            volume: 音量调整，如"+10%", "-5%"
        """
        try:
            # 使用默认声音如果声音不可用
            if voice_id not in self.available_voices:
                default_voice = "zh-CN-XiaoxiaoNeural"
                self.logger.warning(f"声音 {voice_id} 不可用，使用默认声音 {default_voice}")
                voice_id = default_voice
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # 创建通信对象
            communicate = edge_tts.Communicate(text, voice_id, rate=rate, volume=volume)
            
            # 合成语音并保存
            await communicate.save(output_path)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"异步语音合成失败: {str(e)}")
            raise
    
    def synthesize(self, text: str, output_path: str, voice_id: Optional[str] = None, 
                  emotion: Optional[str] = None, speed: float = 1.0) -> str:
        """
        将文本合成为语音
        
        Args:
            text: 待合成的文本
            output_path: 输出文件路径
            voice_id: 声音ID，默认为zh-CN-XiaoxiaoNeural
            emotion: 情感类型（通过SSML标签实现）
            speed: 语速，1.0表示正常语速
            
        Returns:
            生成的音频文件路径
        """
        try:
            # 使用默认声音如果未指定
            if not voice_id:
                voice_id = self.config.get("voice", "zh-CN-XiaoxiaoNeural")
            
            # 转换速度为Edge TTS格式
            rate = f"{int((speed - 1.0) * 100):+d}%"
            
            # 转换音量
            volume = self.config.get("volume", "+0%")
            if not isinstance(volume, str) or not volume.endswith("%"):
                volume = f"{int(float(volume) * 100):+d}%"
            
            # 添加情感SSML（如果支持）
            if emotion and voice_id.endswith("Neural"):
                # 只有Neural声音支持情感调整
                original_text = text
                # 为支持的中文神经网络声音添加情感样式
                if "zh-CN" in voice_id and emotion in self.emotions:
                    style_tag = f'<mstts:express-as style="{emotion}">{text}</mstts:express-as>'
                    text = f'<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" version="1.0">{style_tag}</speak>'
                else:
                    self.logger.warning(f"情感 {emotion} 或声音 {voice_id} 不支持情感调整")
                    text = original_text
            
            # 异步合成语音
            result = asyncio.run(self._synthesize_async(text, output_path, voice_id, rate, volume))
            
            self.logger.info(f"语音合成成功: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"语音合成失败: {str(e)}")
            raise
    
    def clone_voice(self, audio_path: str, voice_name: str) -> str:
        """
        从音频样本克隆声音 (Edge TTS不支持声音克隆)
        
        Args:
            audio_path: 音频样本路径
            voice_name: 声音名称
            
        Returns:
            生成的声音ID
        """
        self.logger.warning("Edge TTS不支持声音克隆功能")
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
            情感ID到情感描述的映射
        """
        return self.emotions
    
    async def get_available_voices_async(self) -> Dict[str, Dict[str, Any]]:
        """
        异步获取最新的可用声音列表
        
        Returns:
            声音ID到声音信息的映射
        """
        await self._load_voices()
        return self.available_voices 