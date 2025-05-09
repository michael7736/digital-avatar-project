#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from typing import Dict, Any, Optional

class ConfigLoader:
    """配置加载器，负责加载和管理系统配置"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.logger = logging.getLogger("ConfigLoader")
        self.config: Dict[str, Any] = {}
        
        # 如果没有提供配置路径，使用默认配置
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       "configs", "default.json")
        
        self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径
        """
        try:
            if not os.path.exists(config_path):
                self.logger.error(f"配置文件不存在: {config_path}")
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.logger.info(f"成功加载配置: {config_path}")
            
            # 加载环境变量配置
            self._load_env_config()
            
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"加载配置时出错: {str(e)}")
            raise
    
    def _load_env_config(self) -> None:
        """从环境变量加载配置，环境变量优先级高于配置文件"""
        # API密钥从环境变量加载
        if 'OPENAI_API_KEY' in os.environ and 'openai' in self.config:
            self.config['openai']['api_key'] = os.environ['OPENAI_API_KEY']
        
        if 'AZURE_SPEECH_KEY' in os.environ and 'azure' in self.config:
            self.config['azure']['speech_key'] = os.environ['AZURE_SPEECH_KEY']
            
        if 'AZURE_SPEECH_REGION' in os.environ and 'azure' in self.config:
            self.config['azure']['speech_region'] = os.environ['AZURE_SPEECH_REGION']
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        获取指定模块的配置
        
        Args:
            module_name: 模块名称
            
        Returns:
            模块配置字典
        """
        if module_name not in self.config:
            self.logger.warning(f"模块 {module_name} 配置不存在，返回空配置")
            return {}
        
        return self.config[module_name]
    
    def save_config(self, config_path: str) -> None:
        """
        保存当前配置到文件
        
        Args:
            config_path: 保存路径
        """
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"成功保存配置: {config_path}")
        except Exception as e:
            self.logger.error(f"保存配置时出错: {str(e)}")
            raise
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新当前配置
        
        Args:
            new_config: 新配置字典
        """
        self.config.update(new_config)
        self.logger.info("配置已更新")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置的便捷函数
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    loader = ConfigLoader(config_path)
    return loader.get_config() 