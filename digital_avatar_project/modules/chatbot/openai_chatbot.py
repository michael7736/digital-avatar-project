#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional, Iterator

import openai
from openai import OpenAI

from .interface import ChatbotInterface


class OpenAIChatbot(ChatbotInterface):
    """
    基于OpenAI API的对话管理实现
    """
    
    def __init__(self):
        self.logger = logging.getLogger("OpenAIChatbot")
        self.client = None
        self.config = {}
        self.history = []
        self.system_message = None
        self.max_history = 10
        self.initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化OpenAI对话管理器
        
        Args:
            config: 配置参数，必须包含api_key
            
        Returns:
            初始化是否成功
        """
        try:
            api_key = config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                self.logger.error("配置中缺少OpenAI API密钥")
                return False
            
            self.config = config
            self.client = OpenAI(api_key=api_key)
            
            # 设置API基础URL（如果有提供）
            if "api_base" in config:
                openai.api_base = config["api_base"]
            
            # 设置系统消息
            self.system_message = {
                "role": "system",
                "content": config.get("system_prompt", "你是一个友好的数字人助手，请用简洁自然的语言回答问题。")
            }
            
            # 设置最大历史长度
            self.max_history = config.get("max_history", 10)
            
            # 测试API连接
            self._test_connection()
            
            self.logger.info("OpenAI Chatbot 初始化成功")
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"初始化OpenAI Chatbot时出错: {str(e)}")
            return False
    
    def _test_connection(self) -> None:
        """测试API连接"""
        try:
            # 创建一个简单的测试请求
            self.client.chat.completions.create(
                model=self.config.get("model", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "你好"},
                    {"role": "user", "content": "测试"}
                ],
                max_tokens=5
            )
            self.logger.info("API连接测试成功")
        except Exception as e:
            self.logger.error(f"API连接测试失败: {str(e)}")
            raise
    
    def _prepare_messages(self, user_input: str) -> List[Dict[str, str]]:
        """
        准备发送给API的消息列表
        
        Args:
            user_input: 用户输入
            
        Returns:
            消息列表
        """
        messages = [self.system_message]
        
        # 添加历史消息，但限制数量
        if len(self.history) > 0:
            messages.extend(self.history[-self.max_history:])
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def get_response(self, user_input: str) -> str:
        """
        获取对用户输入的响应
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            系统响应文本
        """
        if not self.initialized or not self.client:
            raise RuntimeError("OpenAI Chatbot 尚未初始化")
        
        try:
            messages = self._prepare_messages(user_input)
            
            response = self.client.chat.completions.create(
                model=self.config.get("model", "gpt-3.5-turbo"),
                messages=messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 150),
                top_p=self.config.get("top_p", 1.0),
                frequency_penalty=self.config.get("frequency_penalty", 0.0),
                presence_penalty=self.config.get("presence_penalty", 0.0)
            )
            
            reply = response.choices[0].message.content.strip()
            
            # 更新对话历史
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": reply})
            
            # 如果历史太长，移除旧的对话
            if len(self.history) > self.max_history * 2:
                self.history = self.history[-self.max_history * 2:]
            
            return reply
            
        except Exception as e:
            self.logger.error(f"获取OpenAI响应时出错: {str(e)}")
            return f"抱歉，我暂时无法回答您的问题。错误: {str(e)}"
    
    def get_streaming_response(self, user_input: str) -> Iterator[str]:
        """
        获取流式响应迭代器
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            流式响应迭代器
        """
        if not self.initialized or not self.client:
            raise RuntimeError("OpenAI Chatbot 尚未初始化")
        
        try:
            messages = self._prepare_messages(user_input)
            
            # 使用流式API
            response = self.client.chat.completions.create(
                model=self.config.get("model", "gpt-3.5-turbo"),
                messages=messages,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 150),
                top_p=self.config.get("top_p", 1.0),
                frequency_penalty=self.config.get("frequency_penalty", 0.0),
                presence_penalty=self.config.get("presence_penalty", 0.0),
                stream=True
            )
            
            # 收集完整回复
            full_reply = ""
            
            # 更新对话历史（用户部分）
            self.history.append({"role": "user", "content": user_input})
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply += content
                    yield content
            
            # 更新对话历史（助手部分）
            self.history.append({"role": "assistant", "content": full_reply})
            
            # 如果历史太长，移除旧的对话
            if len(self.history) > self.max_history * 2:
                self.history = self.history[-self.max_history * 2:]
            
        except Exception as e:
            self.logger.error(f"获取OpenAI流式响应时出错: {str(e)}")
            yield f"抱歉，我暂时无法回答您的问题。错误: {str(e)}"
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """
        设置对话上下文
        
        Args:
            context: 上下文信息
        """
        if "system_prompt" in context:
            self.system_message = {
                "role": "system",
                "content": context["system_prompt"]
            }
        
        if "max_history" in context:
            self.max_history = context["max_history"]
        
        if "history" in context:
            self.history = context["history"]
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        return self.history
    
    def clear_history(self) -> None:
        """
        清除对话历史
        """
        self.history = []
        self.logger.info("对话历史已清除")
    
    def save_history(self, file_path: str) -> bool:
        """
        保存对话历史到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "history": self.history,
                    "system_message": self.system_message,
                    "timestamp": time.time()
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"对话历史已保存到: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存对话历史时出错: {str(e)}")
            return False
    
    def load_history(self, file_path: str) -> bool:
        """
        从文件加载对话历史
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否加载成功
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"对话历史文件不存在: {file_path}")
                return False
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.history = data.get("history", [])
            
            if "system_message" in data:
                self.system_message = data["system_message"]
            
            self.logger.info(f"对话历史已从 {file_path} 加载")
            return True
            
        except Exception as e:
            self.logger.error(f"加载对话历史时出错: {str(e)}")
            return False 