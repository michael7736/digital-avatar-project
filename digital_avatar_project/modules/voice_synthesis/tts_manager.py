#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
语音合成管理模块
"""

import os
import logging
import tempfile
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class TTSManager:
    """语音合成管理器，支持多种TTS引擎"""
    
    def __init__(self, config):
        """初始化语音合成管理器
        
        Args:
            config (dict): 语音合成配置
        """
        self.config = config
        self.engine_type = config.get("engine", "openai")
        self.engine = self._init_engine()
        self.output_dir = Path(config.get("output_dir", "temp/audio"))
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"语音合成管理器初始化完成, 引擎: {self.engine_type}")
    
    def _init_engine(self):
        """根据配置初始化TTS引擎
        
        Returns:
            object: TTS引擎实例
        """
        if self.engine_type == "openai":
            return self._init_openai_tts()
        elif self.engine_type == "azure":
            return self._init_azure_tts()
        elif self.engine_type == "edge_tts":
            return self._init_edge_tts()
        elif self.engine_type == "coqui":
            return self._init_coqui_tts()
        elif self.engine_type == "custom":
            return self._init_custom_tts()
        else:
            logger.warning(f"未知的TTS引擎类型: {self.engine_type}, 将使用OpenAI TTS")
            return self._init_openai_tts()
    
    def _init_openai_tts(self):
        """初始化OpenAI TTS引擎
        
        Returns:
            object: OpenAI TTS引擎实例
        """
        try:
            import openai
            from openai import OpenAI
            
            api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.error("未提供OpenAI API密钥")
                raise ValueError("未提供OpenAI API密钥")
            
            client = OpenAI(api_key=api_key)
            return client
        
        except ImportError:
            logger.error("未安装openai包，请使用pip install openai进行安装")
            raise
    
    def _init_azure_tts(self):
        """初始化Azure TTS引擎
        
        Returns:
            object: Azure TTS引擎实例
        """
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            subscription_key = self.config.get("subscription_key") or os.environ.get("AZURE_SPEECH_KEY")
            region = self.config.get("region") or os.environ.get("AZURE_SPEECH_REGION")
            
            if not subscription_key or not region:
                logger.error("未提供Azure Speech服务密钥或区域")
                raise ValueError("未提供Azure Speech服务密钥或区域")
            
            speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
            
            # 设置语音
            voice_name = self.config.get("voice", "zh-CN-XiaoxiaoNeural")
            speech_config.speech_synthesis_voice_name = voice_name
            
            return speech_config
        
        except ImportError:
            logger.error("未安装azure-cognitiveservices-speech包，请安装相应依赖")
            raise
    
    def _init_edge_tts(self):
        """初始化Edge TTS引擎
        
        Returns:
            object: Edge TTS引擎实例
        """
        try:
            import edge_tts
            
            voice = self.config.get("voice", "zh-CN-XiaoxiaoNeural")
            return {"voice": voice}
        
        except ImportError:
            logger.error("未安装edge-tts包，请使用pip install edge-tts进行安装")
            raise

    def _init_coqui_tts(self):
        """初始化Coqui TTS引擎 (开源本地部署TTS方案)
        
        Returns:
            object: Coqui TTS引擎实例
        """
        try:
            from TTS.api import TTS
            
            # 获取模型配置
            model_name = self.config.get("model_name", "tts_models/zh-CN/baker/tacotron2-DDC-GST")
            model_path = self.config.get("model_path", None)
            config_path = self.config.get("config_path", None)
            vocoder_path = self.config.get("vocoder_path", None)
            vocoder_config_path = self.config.get("vocoder_config_path", None)
            use_cuda = self.config.get("use_cuda", False)
            
            # 初始化TTS模型
            if model_path and config_path:
                # 使用本地自定义模型
                tts = TTS(
                    model_path=model_path,
                    config_path=config_path,
                    vocoder_path=vocoder_path,
                    vocoder_config_path=vocoder_config_path,
                    use_cuda=use_cuda
                )
                logger.info(f"已加载本地Coqui TTS模型: {model_path}")
            else:
                # 使用预训练模型
                tts = TTS(model_name=model_name, use_cuda=use_cuda)
                logger.info(f"已加载预训练Coqui TTS模型: {model_name}")
            
            return tts
        
        except ImportError:
            logger.error("未安装TTS包，请使用pip install TTS进行安装")
            raise
        except Exception as e:
            logger.error(f"初始化Coqui TTS失败: {str(e)}")
            raise
    
    def _init_custom_tts(self):
        """初始化自定义TTS引擎
        
        Returns:
            object: 自定义TTS引擎实例
        """
        # 自定义TTS实现，可以根据需要自行扩展
        custom_engine_path = self.config.get("custom_engine_path")
        if not custom_engine_path or not Path(custom_engine_path).exists():
            logger.error(f"自定义TTS引擎路径不存在: {custom_engine_path}")
            raise ValueError(f"自定义TTS引擎路径不存在: {custom_engine_path}")
        
        # 导入自定义模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("custom_tts", custom_engine_path)
        custom_tts = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_tts)
        
        return custom_tts.init_engine(self.config)
    
    def synthesize(self, text, output_path=None):
        """合成语音
        
        Args:
            text (str): 待合成的文本
            output_path (str, optional): 输出音频文件路径，若不指定则生成临时文件
        
        Returns:
            str: 合成的音频文件路径
        """
        if not text:
            logger.warning("合成文本为空")
            return None
        
        logger.info(f"开始合成语音: {text[:30]}{'...' if len(text) > 30 else ''}")
        
        # 生成输出路径
        if not output_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"tts_{timestamp}.mp3"
            output_path = self.output_dir / filename
        
        try:
            if self.engine_type == "openai":
                return self._synthesize_openai(text, output_path)
            elif self.engine_type == "azure":
                return self._synthesize_azure(text, output_path)
            elif self.engine_type == "edge_tts":
                return self._synthesize_edge(text, output_path)
            elif self.engine_type == "coqui":
                return self._synthesize_coqui(text, output_path)
            elif self.engine_type == "custom":
                return self._synthesize_custom(text, output_path)
            else:
                logger.warning(f"未知的TTS引擎类型: {self.engine_type}")
                return None
        
        except Exception as e:
            logger.error(f"语音合成失败: {str(e)}")
            return None
    
    def _synthesize_openai(self, text, output_path):
        """使用OpenAI TTS引擎合成语音
        
        Args:
            text (str): 待合成的文本
            output_path (str): 输出音频文件路径
        
        Returns:
            str: 合成的音频文件路径
        """
        voice = self.config.get("voice", "alloy")
        response = self.engine.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        response.stream_to_file(str(output_path))
        logger.info(f"OpenAI TTS 语音合成完成: {output_path}")
        
        return str(output_path)
    
    def _synthesize_azure(self, text, output_path):
        """使用Azure TTS引擎合成语音
        
        Args:
            text (str): 待合成的文本
            output_path (str): 输出音频文件路径
        
        Returns:
            str: 合成的音频文件路径
        """
        import azure.cognitiveservices.speech as speechsdk
        
        # 创建文件配置
        file_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
        
        # 创建语音合成器
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.engine, 
            audio_config=file_config
        )
        
        # 合成语音
        result = speech_synthesizer.speak_text_async(text).get()
        
        # 检查结果
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"Azure TTS 语音合成完成: {output_path}")
            return str(output_path)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Azure TTS 语音合成被取消: {cancellation_details.reason}")
            logger.error(f"错误详情: {cancellation_details.error_details}")
            return None
    
    def _synthesize_edge(self, text, output_path):
        """使用Edge TTS引擎合成语音
        
        Args:
            text (str): 待合成的文本
            output_path (str): 输出音频文件路径
        
        Returns:
            str: 合成的音频文件路径
        """
        import edge_tts
        import asyncio
        
        voice = self.engine.get("voice")
        
        async def _synthesize():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))
        
        asyncio.run(_synthesize())
        logger.info(f"Edge TTS 语音合成完成: {output_path}")
        
        return str(output_path)
    
    def _synthesize_coqui(self, text, output_path):
        """使用Coqui TTS引擎合成语音
        
        Args:
            text (str): 待合成的文本
            output_path (str): 输出音频文件路径
        
        Returns:
            str: 合成的音频文件路径
        """
        # 获取语音配置
        speaker = self.config.get("speaker", None)
        language = self.config.get("language", None)
        
        # 合成语音
        self.engine.tts_to_file(
            text=text,
            file_path=str(output_path),
            speaker=speaker,
            language=language
        )
        
        logger.info(f"Coqui TTS 语音合成完成: {output_path}")
        return str(output_path)
    
    def _synthesize_custom(self, text, output_path):
        """使用自定义TTS引擎合成语音
        
        Args:
            text (str): 待合成的文本
            output_path (str): 输出音频文件路径
        
        Returns:
            str: 合成的音频文件路径
        """
        # 调用自定义引擎的合成方法
        result = self.engine.synthesize(text, str(output_path), self.config)
        logger.info(f"自定义 TTS 语音合成完成: {output_path}")
        
        return result 