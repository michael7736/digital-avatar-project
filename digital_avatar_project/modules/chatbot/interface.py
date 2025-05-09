#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


class ChatbotInterface(ABC):
    """
    对话管理接口
    所有对话管理器实现必须继承该接口
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化对话管理器
        
        Args:
            config: 配置参数
            
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def get_response(self, user_input: str) -> str:
        """
        获取对用户输入的响应
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            系统响应文本
        """
        pass
    
    @abstractmethod
    def get_streaming_response(self, user_input: str) -> Any:
        """
        获取流式响应迭代器
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            流式响应迭代器
        """
        pass
    
    @abstractmethod
    def set_context(self, context: Dict[str, Any]) -> None:
        """
        设置对话上下文
        
        Args:
            context: 上下文信息
        """
        pass
    
    @abstractmethod
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        pass
    
    @abstractmethod
    def clear_history(self) -> None:
        """
        清除对话历史
        """
        pass
    
    @abstractmethod
    def save_history(self, file_path: str) -> bool:
        """
        保存对话历史到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否保存成功
        """
        pass
    
    @abstractmethod
    def load_history(self, file_path: str) -> bool:
        """
        从文件加载对话历史
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否加载成功
        """
        pass 