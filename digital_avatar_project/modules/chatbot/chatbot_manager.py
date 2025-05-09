#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
对话管理模块
"""

import os
import logging
import json
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class ChatbotManager:
    """对话管理器，负责生成回复和管理对话状态"""
    
    def __init__(self, config):
        """初始化对话管理器
        
        Args:
            config (dict): 对话管理配置
        """
        self.config = config
        self.engine_type = config.get("engine", "openai")
        self.max_history = config.get("max_history", 10)
        self.conversation_history = []
        self.system_prompt = config.get("system_prompt", "你是一个友好的数字人助手。")
        
        # 初始化对话引擎
        self.engine = self._init_engine()
        logger.info(f"对话管理器初始化完成, 引擎: {self.engine_type}")
    
    def _init_engine(self):
        """根据配置初始化对话引擎
        
        Returns:
            object: 对话引擎实例
        """
        if self.engine_type == "openai":
            return self._init_openai()
        elif self.engine_type == "langchain":
            return self._init_langchain()
        elif self.engine_type == "custom":
            return self._init_custom_engine()
        else:
            logger.warning(f"未知的对话引擎类型: {self.engine_type}, 将使用OpenAI")
            return self._init_openai()
    
    def _init_openai(self):
        """初始化OpenAI对话引擎
        
        Returns:
            object: OpenAI对话引擎实例
        """
        try:
            import openai
            from openai import OpenAI
            
            api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.error("未提供OpenAI API密钥")
                raise ValueError("未提供OpenAI API密钥")
            
            client = OpenAI(api_key=api_key)
            
            return {
                "client": client,
                "model": self.config.get("model", "gpt-3.5-turbo"),
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 150)
            }
        
        except ImportError:
            logger.error("未安装openai包，请使用pip install openai进行安装")
            raise
    
    def _init_langchain(self):
        """初始化LangChain对话引擎
        
        Returns:
            object: LangChain对话引擎实例
        """
        try:
            from langchain.llms import OpenAI as LangChainOpenAI
            from langchain.chat_models import ChatOpenAI
            from langchain.chains import ConversationChain
            from langchain.memory import ConversationBufferMemory
            
            api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.error("未提供OpenAI API密钥")
                raise ValueError("未提供OpenAI API密钥")
            
            # 设置API密钥
            os.environ["OPENAI_API_KEY"] = api_key
            
            # 创建LLM
            chat_model = ChatOpenAI(
                model_name=self.config.get("model", "gpt-3.5-turbo"),
                temperature=self.config.get("temperature", 0.7)
            )
            
            # 创建记忆
            memory = ConversationBufferMemory()
            
            # 创建对话链
            conversation = ConversationChain(
                llm=chat_model,
                memory=memory,
                verbose=self.config.get("verbose", False)
            )
            
            return {
                "conversation": conversation,
                "memory": memory
            }
        
        except ImportError:
            logger.error("未安装langchain包，请使用pip install langchain进行安装")
            raise
    
    def _init_custom_engine(self):
        """初始化自定义对话引擎
        
        Returns:
            object: 自定义对话引擎实例
        """
        # 自定义引擎实现，可以根据需要自行扩展
        custom_engine_path = self.config.get("custom_engine_path")
        if not custom_engine_path or not Path(custom_engine_path).exists():
            logger.error(f"自定义对话引擎路径不存在: {custom_engine_path}")
            raise ValueError(f"自定义对话引擎路径不存在: {custom_engine_path}")
        
        # 导入自定义模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("custom_chatbot", custom_engine_path)
        custom_chatbot = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_chatbot)
        
        return custom_chatbot.init_engine(self.config)
    
    def add_message(self, role, content):
        """添加消息到对话历史
        
        Args:
            role (str): 消息角色，可以是"user"、"assistant"或"system"
            content (str): 消息内容
        """
        message = {"role": role, "content": content, "timestamp": time.time()}
        self.conversation_history.append(message)
        
        # 限制历史记录长度
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def generate_response(self, user_input=None):
        """生成回复
        
        Args:
            user_input (str, optional): 用户输入，如果为None则使用模拟输入
        
        Returns:
            str: 生成的回复
        """
        # 如果没有用户输入，使用模拟输入
        if user_input is None:
            user_input = self._generate_simulated_input()
        
        # 添加用户消息到历史
        self.add_message("user", user_input)
        
        try:
            if self.engine_type == "openai":
                response = self._generate_openai_response(user_input)
            elif self.engine_type == "langchain":
                response = self._generate_langchain_response(user_input)
            elif self.engine_type == "custom":
                response = self._generate_custom_response(user_input)
            else:
                logger.warning(f"未知的对话引擎类型: {self.engine_type}")
                response = "抱歉，我现在无法回答你的问题。"
            
            # 添加助手回复到历史
            self.add_message("assistant", response)
            
            return response
        
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")
            return "抱歉，我现在遇到了一些问题，无法回答你的问题。"
    
    def _generate_openai_response(self, user_input):
        """使用OpenAI生成回复
        
        Args:
            user_input (str): 用户输入
        
        Returns:
            str: 生成的回复
        """
        client = self.engine["client"]
        
        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加历史对话
        for msg in self.conversation_history[:-1]:  # 排除最后一条，因为是当前用户输入
            if msg["role"] in ["user", "assistant", "system"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        # 调用API
        response = client.chat.completions.create(
            model=self.engine["model"],
            messages=messages,
            temperature=self.engine["temperature"],
            max_tokens=self.engine["max_tokens"]
        )
        
        # 返回回复内容
        return response.choices[0].message.content
    
    def _generate_langchain_response(self, user_input):
        """使用LangChain生成回复
        
        Args:
            user_input (str): 用户输入
        
        Returns:
            str: 生成的回复
        """
        conversation = self.engine["conversation"]
        
        # 添加系统提示
        if not hasattr(conversation, '_added_system_prompt'):
            conversation.memory.chat_memory.add_user_message(f"系统说明: {self.system_prompt}")
            conversation.memory.chat_memory.add_ai_message("我明白了，我会按照这个要求来回答用户的问题。")
            conversation._added_system_prompt = True
        
        # 生成回复
        response = conversation.predict(input=user_input)
        
        return response
    
    def _generate_custom_response(self, user_input):
        """使用自定义引擎生成回复
        
        Args:
            user_input (str): 用户输入
        
        Returns:
            str: 生成的回复
        """
        # 调用自定义引擎的生成方法
        return self.engine.generate_response(
            user_input,
            self.conversation_history,
            self.system_prompt,
            self.config
        )
    
    def _generate_simulated_input(self):
        """生成模拟用户输入
        
        Returns:
            str: 模拟用户输入
        """
        # 如果配置了模拟输入列表，从中随机选择一个
        simulated_inputs = self.config.get("simulated_inputs", [
            "你好，我想了解一下今天的天气。",
            "给我讲个笑话吧。",
            "你能做什么？",
            "推荐一部电影给我。",
            "今天是几号？"
        ])
        
        import random
        return random.choice(simulated_inputs)
    
    def save_conversation(self, file_path=None):
        """保存对话历史
        
        Args:
            file_path (str, optional): 保存文件路径，如果不指定则使用时间戳命名
        
        Returns:
            str: 保存的文件路径
        """
        if not file_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = f"conversation_{timestamp}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        
        logger.info(f"对话历史已保存到: {file_path}")
        return file_path
    
    def load_conversation(self, file_path):
        """加载对话历史
        
        Args:
            file_path (str): 加载文件路径
        
        Returns:
            bool: 加载是否成功
        """
        if not Path(file_path).exists():
            logger.error(f"对话历史文件不存在: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            
            logger.info(f"对话历史已加载: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"加载对话历史失败: {str(e)}")
            return False
    
    def clear_conversation(self):
        """清空对话历史"""
        self.conversation_history = []
        logger.info("对话历史已清空") 