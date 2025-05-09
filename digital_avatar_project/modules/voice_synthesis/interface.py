#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class VoiceSynthesizer(ABC):
    """
    语音合成接口
    所有语音合成器实现必须继承该接口
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化语音合成器
        
        Args:
            config: 配置参数
            
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def synthesize(self, text: str, output_path: str, voice_id: Optional[str] = None, 
                  emotion: Optional[str] = None, speed: float = 1.0) -> str:
        """
        将文本合成为语音
        
        Args:
            text: 待合成的文本
            output_path: 输出文件路径
            voice_id: 声音ID
            emotion: 情感类型
            speed: 语速
            
        Returns:
            生成的音频文件路径
        """
        pass
    
    @abstractmethod
    def clone_voice(self, audio_path: str, voice_name: str) -> str:
        """
        从音频样本克隆声音
        
        Args:
            audio_path: 音频样本路径
            voice_name: 声音名称
            
        Returns:
            生成的声音ID
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        获取可用的声音列表
        
        Returns:
            声音ID到声音信息的映射
        """
        pass
    
    @abstractmethod
    def get_emotions(self) -> Dict[str, str]:
        """
        获取支持的情感类型
        
        Returns:
            情感ID到情感描述的映射
        """
        pass 