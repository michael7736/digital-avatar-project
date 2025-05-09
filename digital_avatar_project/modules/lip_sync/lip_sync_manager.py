#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
唇语同步管理模块
"""

import os
import logging
import tempfile
import subprocess
import numpy as np
import cv2
from pathlib import Path
import time
import shutil

logger = logging.getLogger(__name__)

class LipSyncManager:
    """唇语同步管理器，负责生成与音频同步的唇部动画"""
    
    def __init__(self, config):
        """初始化唇语同步管理器
        
        Args:
            config (dict): 唇语同步配置
        """
        self.config = config
        self.engine_type = config.get("engine", "wav2lip")
        self.smooth_factor = config.get("smooth_factor", 0.5)
        self.frame_rate = config.get("frame_rate", 30)
        self.output_dir = Path(config.get("output_dir", "temp/videos"))
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化唇语同步引擎
        self.engine = self._init_engine()
        logger.info(f"唇语同步管理器初始化完成, 引擎: {self.engine_type}")
    
    def _init_engine(self):
        """根据配置初始化唇语同步引擎
        
        Returns:
            object: 唇语同步引擎实例
        """
        if self.engine_type == "wav2lip":
            return self._init_wav2lip()
        elif self.engine_type == "sad_talker":
            return self._init_sad_talker()
        elif self.engine_type == "custom":
            return self._init_custom_engine()
        else:
            logger.warning(f"未知的唇语同步引擎类型: {self.engine_type}, 将使用Wav2Lip")
            return self._init_wav2lip()
    
    def _init_wav2lip(self):
        """初始化Wav2Lip引擎
        
        Returns:
            object: Wav2Lip引擎实例
        """
        try:
            # 检查是否有Wav2Lip配置
            wav2lip_path = self.config.get("wav2lip_path")
            if not wav2lip_path or not Path(wav2lip_path).exists():
                logger.warning("未指定Wav2Lip路径或路径不存在，将使用命令行方式调用")
                return {"type": "command_line"}
            
            # 如果有模型权重配置，确认文件存在
            checkpoint_path = self.config.get("checkpoint_path")
            if checkpoint_path and not Path(checkpoint_path).exists():
                logger.error(f"Wav2Lip模型权重文件不存在: {checkpoint_path}")
                return {"type": "command_line"}
            
            # 返回配置
            return {
                "type": "module",
                "path": wav2lip_path,
                "checkpoint": checkpoint_path
            }
            
        except Exception as e:
            logger.error(f"初始化Wav2Lip引擎失败: {str(e)}")
            return {"type": "command_line"}
    
    def _init_sad_talker(self):
        """初始化SadTalker引擎
        
        Returns:
            object: SadTalker引擎实例
        """
        try:
            # 检查是否有SadTalker配置
            sad_talker_path = self.config.get("sad_talker_path")
            if not sad_talker_path or not Path(sad_talker_path).exists():
                logger.warning("未指定SadTalker路径或路径不存在，将使用命令行方式调用")
                return {"type": "command_line"}
            
            # 如果有预训练模型配置，确认文件存在
            checkpoints_dir = self.config.get("checkpoints_dir")
            if checkpoints_dir and not Path(checkpoints_dir).exists():
                logger.error(f"SadTalker预训练模型目录不存在: {checkpoints_dir}")
                return {"type": "command_line"}
            
            # 返回配置
            return {
                "type": "module",
                "path": sad_talker_path,
                "checkpoints_dir": checkpoints_dir
            }
            
        except Exception as e:
            logger.error(f"初始化SadTalker引擎失败: {str(e)}")
            return {"type": "command_line"}
    
    def _init_custom_engine(self):
        """初始化自定义唇语同步引擎
        
        Returns:
            object: 自定义唇语同步引擎实例
        """
        # 自定义引擎实现，可以根据需要自行扩展
        custom_engine_path = self.config.get("custom_engine_path")
        if not custom_engine_path or not Path(custom_engine_path).exists():
            logger.error(f"自定义唇语同步引擎路径不存在: {custom_engine_path}")
            raise ValueError(f"自定义唇语同步引擎路径不存在: {custom_engine_path}")
        
        # 导入自定义模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("custom_lip_sync", custom_engine_path)
        custom_lip_sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_lip_sync)
        
        return custom_lip_sync.init_engine(self.config)
    
    def generate(self, source_image, audio_file):
        """生成唇语同步视频
        
        Args:
            source_image (np.ndarray): 源图像
            audio_file (str): 音频文件路径
        
        Returns:
            str: 生成的视频文件路径
        """
        if not Path(audio_file).exists():
            logger.error(f"音频文件不存在: {audio_file}")
            return None
        
        # 生成输出视频路径
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_video = self.output_dir / f"lip_sync_{timestamp}.mp4"
        
        try:
            if self.engine_type == "wav2lip":
                return self._generate_wav2lip(source_image, audio_file, output_video)
            elif self.engine_type == "sad_talker":
                return self._generate_sad_talker(source_image, audio_file, output_video)
            elif self.engine_type == "custom":
                return self._generate_custom(source_image, audio_file, output_video)
            else:
                logger.warning(f"未知的唇语同步引擎类型: {self.engine_type}")
                return None
            
        except Exception as e:
            logger.error(f"生成唇语同步视频失败: {str(e)}")
            return None
    
    def _generate_wav2lip(self, source_image, audio_file, output_video):
        """使用Wav2Lip生成唇语同步视频
        
        Args:
            source_image (np.ndarray): 源图像
            audio_file (str): 音频文件路径
            output_video (str): 输出视频路径
        
        Returns:
            str: 生成的视频文件路径
        """
        # 保存源图像为临时文件
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
            temp_img_path = temp_img.name
            cv2.imwrite(temp_img_path, cv2.cvtColor(source_image, cv2.COLOR_RGB2BGR))
        
        try:
            if self.engine["type"] == "module":
                return self._generate_wav2lip_module(temp_img_path, audio_file, output_video)
            else:
                return self._generate_wav2lip_cmd(temp_img_path, audio_file, output_video)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_img_path):
                os.unlink(temp_img_path)
    
    def _generate_wav2lip_module(self, image_path, audio_path, output_path):
        """使用Wav2Lip模块生成唇语同步视频
        
        Args:
            image_path (str): 源图像路径
            audio_path (str): 音频文件路径
            output_path (str): 输出视频路径
        
        Returns:
            str: 生成的视频文件路径
        """
        # 将Wav2Lip目录添加到sys.path
        import sys
        wav2lip_path = self.engine["path"]
        if wav2lip_path not in sys.path:
            sys.path.append(wav2lip_path)
        
        # 导入Wav2Lip所需模块
        from inference import load_model, datagen, write_video
        
        # 加载模型
        checkpoint_path = self.engine["checkpoint"]
        model = load_model(checkpoint_path)
        
        # 生成唇语同步视频
        frames = datagen(image_path, audio_path)
        write_video(frames, audio_path, output_path)
        
        logger.info(f"Wav2Lip模块生成唇语同步视频完成: {output_path}")
        return str(output_path)
    
    def _generate_wav2lip_cmd(self, image_path, audio_path, output_path):
        """使用命令行方式调用Wav2Lip生成唇语同步视频
        
        Args:
            image_path (str): 源图像路径
            audio_path (str): 音频文件路径
            output_path (str): 输出视频路径
        
        Returns:
            str: 生成的视频文件路径
        """
        # 构建命令
        cmd = [
            "python", 
            self.config.get("inference_script", "inference.py"),
            "--checkpoint_path", self.config.get("checkpoint_path", "checkpoints/wav2lip_gan.pth"),
            "--face", image_path,
            "--audio", audio_path,
            "--outfile", str(output_path)
        ]
        
        # 添加其他参数
        if self.config.get("face_det_batch_size"):
            cmd.extend(["--face_det_batch_size", str(self.config.get("face_det_batch_size"))])
        
        if self.config.get("wav2lip_batch_size"):
            cmd.extend(["--wav2lip_batch_size", str(self.config.get("wav2lip_batch_size"))])
        
        if self.config.get("no_smooth"):
            cmd.append("--nosmooth")
        
        if self.config.get("pads"):
            cmd.extend(["--pads", self.config.get("pads")])
        
        # 执行命令
        logger.info(f"执行Wav2Lip命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Wav2Lip命令执行失败: {result.stderr}")
            return None
        
        logger.info(f"Wav2Lip命令行生成唇语同步视频完成: {output_path}")
        return str(output_path)
    
    def _generate_sad_talker(self, source_image, audio_file, output_video):
        """使用SadTalker生成唇语同步视频
        
        Args:
            source_image (np.ndarray): 源图像
            audio_file (str): 音频文件路径
            output_video (str): 输出视频路径
        
        Returns:
            str: 生成的视频文件路径
        """
        # 保存源图像为临时文件
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
            temp_img_path = temp_img.name
            cv2.imwrite(temp_img_path, cv2.cvtColor(source_image, cv2.COLOR_RGB2BGR))
        
        try:
            if self.engine["type"] == "module":
                return self._generate_sad_talker_module(temp_img_path, audio_file, output_video)
            else:
                return self._generate_sad_talker_cmd(temp_img_path, audio_file, output_video)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_img_path):
                os.unlink(temp_img_path)
    
    def _generate_sad_talker_module(self, image_path, audio_path, output_path):
        """使用SadTalker模块生成唇语同步视频
        
        Args:
            image_path (str): 源图像路径
            audio_path (str): 音频文件路径
            output_path (str): 输出视频路径
        
        Returns:
            str: 生成的视频文件路径
        """
        # 将SadTalker目录添加到sys.path
        import sys
        sad_talker_path = self.engine["path"]
        if sad_talker_path not in sys.path:
            sys.path.append(sad_talker_path)
        
        # 导入SadTalker所需模块（假设有一个inference.py模块）
        import inference
        
        # 设置参数
        args = {
            "source_image": image_path,
            "driven_audio": audio_path,
            "result_dir": os.path.dirname(output_path),
            "still": True,
            "preprocess": "full",
            "enhancer": None
        }
        
        # 生成唇语同步视频
        result_video = inference.main(args)
        
        # 如果生成的视频不是我们期望的路径，复制过来
        if result_video != str(output_path):
            shutil.copy(result_video, str(output_path))
        
        logger.info(f"SadTalker模块生成唇语同步视频完成: {output_path}")
        return str(output_path)
    
    def _generate_sad_talker_cmd(self, image_path, audio_path, output_path):
        """使用命令行方式调用SadTalker生成唇语同步视频
        
        Args:
            image_path (str): 源图像路径
            audio_path (str): 音频文件路径
            output_path (str): 输出视频路径
        
        Returns:
            str: 生成的视频文件路径
        """
        # 设置结果目录
        result_dir = os.path.dirname(output_path)
        
        # 构建命令
        cmd = [
            "python", 
            self.config.get("inference_script", "inference.py"),
            "--source_image", image_path,
            "--driven_audio", audio_path,
            "--result_dir", result_dir,
            "--still"
        ]
        
        # 添加预处理参数
        preprocess = self.config.get("preprocess", "full")
        cmd.extend(["--preprocess", preprocess])
        
        # 如果配置了enhancer，添加到命令中
        enhancer = self.config.get("enhancer")
        if enhancer:
            cmd.extend(["--enhancer", enhancer])
        
        # 执行命令
        logger.info(f"执行SadTalker命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"SadTalker命令执行失败: {result.stderr}")
            return None
        
        # SadTalker可能会生成不同名称的输出文件，需要找到它并重命名
        # 这里简化处理，假设输出文件在结果目录中且是最新的视频文件
        result_files = list(Path(result_dir).glob("*.mp4"))
        if not result_files:
            logger.error("SadTalker未生成视频文件")
            return None
        
        # 获取最新的视频文件
        result_file = max(result_files, key=os.path.getctime)
        
        # 如果生成的视频不是我们期望的路径，重命名它
        if str(result_file) != str(output_path):
            shutil.move(str(result_file), str(output_path))
        
        logger.info(f"SadTalker命令行生成唇语同步视频完成: {output_path}")
        return str(output_path)
    
    def _generate_custom(self, source_image, audio_file, output_video):
        """使用自定义引擎生成唇语同步视频
        
        Args:
            source_image (np.ndarray): 源图像
            audio_file (str): 音频文件路径
            output_video (str): 输出视频路径
        
        Returns:
            str: 生成的视频文件路径
        """
        # 保存源图像为临时文件
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
            temp_img_path = temp_img.name
            cv2.imwrite(temp_img_path, cv2.cvtColor(source_image, cv2.COLOR_RGB2BGR))
        
        try:
            # 调用自定义引擎的生成方法
            result = self.engine.generate(
                temp_img_path, 
                audio_file, 
                str(output_video), 
                self.config
            )
            
            logger.info(f"自定义引擎生成唇语同步视频完成: {output_video}")
            return result
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_img_path):
                os.unlink(temp_img_path)
    
    def add_audio_to_video(self, video_file, audio_file, output_file=None):
        """将音频添加到视频
        
        Args:
            video_file (str): 视频文件路径
            audio_file (str): 音频文件路径
            output_file (str, optional): 输出文件路径，若不指定则覆盖原视频
        
        Returns:
            str: 处理后的视频文件路径
        """
        if not output_file:
            # 生成临时输出文件
            output_file = str(Path(video_file).with_suffix('.new.mp4'))
        
        # 使用FFmpeg合并视频和音频
        cmd = [
            "ffmpeg",
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y",
            output_file
        ]
        
        logger.info(f"执行FFmpeg命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg命令执行失败: {result.stderr}")
            return video_file
        
        # 如果没有指定输出文件，则覆盖原视频
        if output_file != video_file:
            shutil.move(output_file, video_file)
            return video_file
        
        return output_file 