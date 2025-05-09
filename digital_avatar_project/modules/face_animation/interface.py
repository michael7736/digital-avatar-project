#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


class AvatarRenderer(ABC):
    """
    虚拟形象渲染接口
    所有虚拟形象渲染器实现必须继承该接口
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化虚拟形象渲染器
        
        Args:
            config: 配置参数
            
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def load_avatar(self, avatar_path: str) -> bool:
        """
        加载虚拟形象
        
        Args:
            avatar_path: 虚拟形象文件路径
            
        Returns:
            是否加载成功
        """
        pass
    
    @abstractmethod
    def render_frame(self, frame_index: int, **kwargs) -> Any:
        """
        渲染单帧
        
        Args:
            frame_index: 帧索引
            **kwargs: 附加参数
            
        Returns:
            渲染结果
        """
        pass
    
    @abstractmethod
    def render_sequence(self, start_frame: int, end_frame: int, output_path: str, **kwargs) -> str:
        """
        渲染序列
        
        Args:
            start_frame: 起始帧
            end_frame: 结束帧
            output_path: 输出路径
            **kwargs: 附加参数
            
        Returns:
            输出文件路径
        """
        pass
    
    @abstractmethod
    def animate(self, animation_type: str, **kwargs) -> bool:
        """
        应用动画
        
        Args:
            animation_type: 动画类型
            **kwargs: 动画参数
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def get_avatar_info(self) -> Dict[str, Any]:
        """
        获取虚拟形象信息
        
        Returns:
            虚拟形象信息
        """
        pass
    
    @abstractmethod
    def get_supported_features(self) -> Dict[str, Any]:
        """
        获取支持的特性
        
        Returns:
            特性信息
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        清理资源
        """
        pass 