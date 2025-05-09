#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地TTS引擎示例脚本
"""

import os
import sys
import yaml
import logging

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from modules.voice_synthesis.tts_manager import TTSManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def load_config(config_path):
    """加载配置文件
    
    Args:
        config_path (str): 配置文件路径
    
    Returns:
        dict: 配置字典
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def main():
    """主函数"""
    # 加载配置
    config_path = os.path.join(project_root, 'config', 'tts_config_local.yaml')
    
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        print("请先创建配置文件，参考示例配置: config/tts_config_local.yaml")
        return
    
    config = load_config(config_path)
    
    # 初始化TTS管理器
    tts_manager = TTSManager(config)
    
    # 准备测试文本
    test_texts = [
        "这是一个本地部署的语音合成引擎测试",
        "Coqui TTS是一个高质量的开源语音合成系统",
        "您可以使用它来构建自己的数字人声音",
        "支持多种语言和声音模型，可以完全本地化部署",
    ]
    
    # 合成测试
    print("开始语音合成测试...")
    for i, text in enumerate(test_texts):
        print(f"[{i+1}/{len(test_texts)}] 合成: {text}")
        output_path = tts_manager.synthesize(text)
        
        if output_path:
            print(f"合成成功，音频文件: {output_path}")
            # 可选：播放音频
            try:
                from playsound import playsound
                playsound(output_path)
            except ImportError:
                print("提示: 安装playsound包可以自动播放合成的音频 (pip install playsound)")
        else:
            print("合成失败")
    
    print("测试完成!")

if __name__ == "__main__":
    main() 