#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple


class StreamingInterface(ABC):
    """
    直播流接口
    所有直播流实现必须继承该接口
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化直播流
        
        Args:
            config: 配置参数
            
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def start_streaming(self) -> bool:
        """
        开始直播
        
        Returns:
            是否成功开始直播
        """
        pass
    
    @abstractmethod
    def stop_streaming(self) -> bool:
        """
        停止直播
        
        Returns:
            是否成功停止直播
        """
        pass
    
    @abstractmethod
    def is_streaming(self) -> bool:
        """
        检查是否正在直播
        
        Returns:
            是否正在直播
        """
        pass
    
    @abstractmethod
    def send_frame(self, frame: Any) -> bool:
        """
        发送视频帧
        
        Args:
            frame: 视频帧数据
            
        Returns:
            是否成功发送
        """
        pass
    
    @abstractmethod
    def send_audio(self, audio_data: Any) -> bool:
        """
        发送音频数据
        
        Args:
            audio_data: 音频数据
            
        Returns:
            是否成功发送
        """
        pass
    
    @abstractmethod
    def send_video(self, video_path: str) -> bool:
        """
        发送视频文件
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            是否成功发送
        """
        pass
    
    @abstractmethod
    def get_stream_info(self) -> Dict[str, Any]:
        """
        获取流信息
        
        Returns:
            流信息字典
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        清理资源
        """
        pass 