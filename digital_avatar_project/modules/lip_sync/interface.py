#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class LipSyncer(ABC):
    """
    唇语同步接口
    所有唇语同步器实现必须继承该接口
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化唇语同步器
        
        Args:
            config: 配置参数
            
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def synchronize(self, audio_path: str, image_path: str, output_path: str,
                   enhance: bool = True, smooth: float = 0.5) -> str:
        """
        将音频与图像同步，生成嘴唇动作
        
        Args:
            audio_path: 音频文件路径
            image_path: 参考图像路径
            output_path: 输出视频文件路径
            enhance: 是否增强视频质量
            smooth: 平滑因子，0-1之间
            
        Returns:
            生成的视频文件路径
        """
        pass
    
    @abstractmethod
    def batch_synchronize(self, audio_paths: List[str], image_paths: List[str], 
                         output_paths: List[str], enhance: bool = True,
                         smooth: float = 0.5) -> List[str]:
        """
        批量处理多个音频和图像
        
        Args:
            audio_paths: 音频文件路径列表
            image_paths: 参考图像路径列表
            output_paths: 输出视频文件路径列表
            enhance: 是否增强视频质量
            smooth: 平滑因子，0-1之间
            
        Returns:
            生成的视频文件路径列表
        """
        pass
    
    @abstractmethod
    def get_supported_features(self) -> Dict[str, Any]:
        """
        获取该同步器支持的特性
        
        Returns:
            特性信息字典
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        清理临时文件和资源
        """
        pass 