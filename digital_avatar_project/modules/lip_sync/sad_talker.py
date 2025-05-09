#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path

from .interface import LipSyncer


class SadTalker(LipSyncer):
    """
    使用SadTalker进行唇语同步的实现
    SadTalker: https://github.com/OpenTalker/SadTalker
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SadTalker")
        self.config = {}
        self.sad_talker_path = None
        self.initialized = False
        self.supported_features = {
            "enhancers": ["gfpgan", "RestoreFormer"],
            "preprocess": ["crop", "full", "resize", "reference"],
            "face_detection": ["retinaface", "mediapipe"],
            "audio_features": ["deepspeech", "hubert"],
            "pose_style": list(range(46))  # 0-45的姿势风格
        }
        self.temp_dir = tempfile.mkdtemp(prefix="sadtalker_")
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化SadTalker
        
        Args:
            config: 配置参数，必须包含sad_talker_path
            
        Returns:
            初始化是否成功
        """
        try:
            if not config.get("sad_talker_path"):
                self.logger.error("配置中缺少SadTalker路径")
                return False
            
            self.config = config
            self.sad_talker_path = Path(config["sad_talker_path"])
            
            # 验证SadTalker路径是否存在
            if not self.sad_talker_path.exists():
                self.logger.error(f"SadTalker路径不存在: {self.sad_talker_path}")
                return False
            
            # 验证推理脚本是否存在
            inference_script = self.sad_talker_path / (config.get("inference_script") or "inference.py")
            if not inference_script.exists():
                self.logger.error(f"SadTalker推理脚本不存在: {inference_script}")
                return False
            
            # 验证检查点目录是否存在
            checkpoints_dir = self.sad_talker_path / (config.get("checkpoints_dir") or "checkpoints")
            if not checkpoints_dir.exists():
                self.logger.warning(f"SadTalker检查点目录不存在: {checkpoints_dir}，可能需要下载模型")
            
            self.logger.info("SadTalker 初始化成功")
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"初始化SadTalker时出错: {str(e)}")
            return False
    
    def _run_sad_talker_command(self, audio_path: str, image_path: str, output_path: str,
                              enhance: bool = True, smooth: float = 0.5) -> str:
        """
        运行SadTalker命令
        
        Args:
            audio_path: 音频文件路径
            image_path: 参考图像路径
            output_path: 输出视频文件路径
            enhance: 是否增强视频质量
            smooth: 平滑因子，0-1之间
            
        Returns:
            生成的视频文件路径
        """
        if not self.initialized:
            raise RuntimeError("SadTalker 尚未初始化")
        
        try:
            # 确保输出目录存在
            output_dir = Path(output_path).parent
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建命令参数
            cmd = [
                sys.executable,
                str(self.sad_talker_path / (self.config.get("inference_script") or "inference.py")),
                "--driven_audio", str(audio_path),
                "--source_image", str(image_path),
                "--result_dir", str(output_dir),
                "--still",  # 使用静态模式
                "--expression_scale", "1.0",  # 表情比例
                "--pose_style", str(self.config.get("pose_style", "0")),  # 默认姿势风格
                "--batch_size", "1",
                "--size", str(self.config.get("image_size", "512")),
                "--preprocess", self.config.get("preprocess", "full"),
                "--face_detector", self.config.get("face_detector", "retinaface")
            ]
            
            # 添加增强器参数
            if enhance:
                enhancer = self.config.get("enhancer", "gfpgan")
                cmd.extend(["--enhancer", enhancer])
            
            # 添加平滑参数
            if smooth > 0:
                cmd.extend(["--smooth", str(smooth)])
            
            # 获取输出文件名（不带路径）
            output_name = Path(output_path).name
            base_name = output_name.split('.')[0]
            cmd.extend(["--result_video", base_name])
            
            # 运行命令
            self.logger.info(f"运行SadTalker命令: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.sad_talker_path),
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"SadTalker命令执行失败: {stderr}")
                raise RuntimeError(f"SadTalker命令执行失败: {stderr}")
            
            # 找到生成的视频文件
            expected_output = output_dir / f"{base_name}.mp4"
            
            if not expected_output.exists():
                self.logger.error(f"SadTalker生成的视频文件不存在: {expected_output}")
                raise FileNotFoundError(f"SadTalker生成的视频文件不存在: {expected_output}")
            
            # 如果输出路径与预期输出不同，则进行复制
            if str(expected_output) != output_path:
                import shutil
                shutil.copy(str(expected_output), output_path)
                os.remove(str(expected_output))  # 移除临时文件
            
            self.logger.info(f"SadTalker生成视频成功: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"运行SadTalker命令时出错: {str(e)}")
            raise
    
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
        return self._run_sad_talker_command(audio_path, image_path, output_path, enhance, smooth)
    
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
        if len(audio_paths) != len(image_paths) or len(audio_paths) != len(output_paths):
            raise ValueError("音频路径、图像路径和输出路径的数量必须相同")
        
        results = []
        for audio_path, image_path, output_path in zip(audio_paths, image_paths, output_paths):
            result = self.synchronize(audio_path, image_path, output_path, enhance, smooth)
            results.append(result)
        
        return results
    
    def get_supported_features(self) -> Dict[str, Any]:
        """
        获取该同步器支持的特性
        
        Returns:
            特性信息字典
        """
        return self.supported_features
    
    def cleanup(self) -> None:
        """
        清理临时文件和资源
        """
        import shutil
        
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"已清理临时目录: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"清理临时文件时出错: {str(e)}")
            
    def __del__(self):
        """析构函数，确保清理临时资源"""
        self.cleanup() 