#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .interface import AvatarRenderer


class ImageAvatar(AvatarRenderer):
    """
    基于图像的2D虚拟形象渲染器
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ImageAvatar")
        self.config = {}
        self.avatar_image = None
        self.avatar_path = None
        self.avatar_info = {}
        self.temp_dir = tempfile.mkdtemp(prefix="avatar_")
        self.frame_cache = {}
        self.animation_state = {}
        
        self.supported_features = {
            "formats": ["png", "jpg", "jpeg"],
            "animations": ["blink", "nod", "shake", "smile"],
            "effects": ["zoom", "fade", "blur"]
        }
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化虚拟形象渲染器
        
        Args:
            config: 配置参数
            
        Returns:
            初始化是否成功
        """
        try:
            self.config = config
            
            # 如果提供了虚拟形象路径，立即加载
            if "avatar_path" in config:
                self.load_avatar(config["avatar_path"])
            
            self.logger.info("2D虚拟形象渲染器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化2D虚拟形象渲染器时出错: {str(e)}")
            return False
    
    def load_avatar(self, avatar_path: str) -> bool:
        """
        加载虚拟形象
        
        Args:
            avatar_path: 虚拟形象文件路径
            
        Returns:
            是否加载成功
        """
        try:
            if not os.path.exists(avatar_path):
                self.logger.error(f"虚拟形象文件不存在: {avatar_path}")
                return False
            
            # 支持格式检查
            file_ext = os.path.splitext(avatar_path)[1].lower().replace(".", "")
            if file_ext not in self.supported_features["formats"]:
                self.logger.error(f"不支持的虚拟形象格式: {file_ext}")
                return False
            
            # 加载图像
            img = cv2.imread(avatar_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                self.logger.error(f"无法加载虚拟形象图像: {avatar_path}")
                return False
            
            # 转换为RGBA格式
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
            
            self.avatar_image = img
            self.avatar_path = avatar_path
            
            # 更新虚拟形象信息
            self.avatar_info = {
                "path": avatar_path,
                "width": img.shape[1],
                "height": img.shape[0],
                "format": file_ext,
                "has_alpha": img.shape[2] == 4
            }
            
            # 清除缓存
            self.frame_cache.clear()
            
            self.logger.info(f"虚拟形象已加载: {avatar_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"加载虚拟形象时出错: {str(e)}")
            return False
    
    def render_frame(self, frame_index: int, **kwargs) -> np.ndarray:
        """
        渲染单帧
        
        Args:
            frame_index: 帧索引
            **kwargs: 附加参数
                - width: 输出宽度
                - height: 输出高度
                - background_color: 背景颜色 (R,G,B,A)
                - animations: 动画参数字典
            
        Returns:
            渲染结果图像
        """
        if self.avatar_image is None:
            raise RuntimeError("尚未加载虚拟形象")
        
        # 检查缓存
        cache_key = f"{frame_index}_{hash(str(kwargs))}"
        if cache_key in self.frame_cache:
            return self.frame_cache[cache_key]
        
        try:
            # 获取输出尺寸
            width = kwargs.get("width", self.avatar_info["width"])
            height = kwargs.get("height", self.avatar_info["height"])
            
            # 创建背景
            background_color = kwargs.get("background_color", (0, 0, 0, 0))
            frame = np.zeros((height, width, 4), dtype=np.uint8)
            frame[:, :] = background_color
            
            # 应用动画
            animations = kwargs.get("animations", {})
            img = self._apply_animations(self.avatar_image.copy(), frame_index, animations)
            
            # 调整大小
            if img.shape[0] != height or img.shape[1] != width:
                img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LANCZOS4)
            
            # 合成图像
            if img.shape[2] == 4:  # 带透明通道
                alpha = img[:, :, 3] / 255.0
                for c in range(3):
                    frame[:, :, c] = frame[:, :, c] * (1 - alpha) + img[:, :, c] * alpha
                frame[:, :, 3] = np.maximum(frame[:, :, 3], img[:, :, 3])
            else:
                frame = img
            
            # 缓存结果
            self.frame_cache[cache_key] = frame
            
            return frame
            
        except Exception as e:
            self.logger.error(f"渲染帧时出错: {str(e)}")
            # 返回空白帧
            return np.zeros((height, width, 4), dtype=np.uint8)
    
    def _apply_animations(self, img: np.ndarray, frame_index: int, animations: Dict[str, Any]) -> np.ndarray:
        """
        应用动画效果
        
        Args:
            img: 原始图像
            frame_index: 帧索引
            animations: 动画参数
        
        Returns:
            处理后的图像
        """
        # 眨眼动画
        if "blink" in animations and animations["blink"]:
            blink_cycle = animations.get("blink_cycle", 90)  # 默认90帧一个周期
            blink_duration = animations.get("blink_duration", 10)  # 默认10帧完成眨眼
            
            phase = frame_index % blink_cycle
            if phase < blink_duration:
                # 计算眨眼程度，0=完全睁开，1=完全闭上
                blink_factor = np.sin(phase / blink_duration * np.pi) if phase < blink_duration / 2 else np.sin((blink_duration - phase) / blink_duration * np.pi)
                
                # 获取眼睛区域（简化处理，假设在图像上半部分中间）
                h, w = img.shape[:2]
                eye_region_y = int(h * 0.25)
                eye_region_h = int(h * 0.15)
                eye_region = img[eye_region_y:eye_region_y+eye_region_h, :, :]
                
                # 向中心挤压
                squeeze_factor = blink_factor * 0.5
                M = np.float32([[1, 0, 0], [0, 1-squeeze_factor, squeeze_factor * eye_region_h / 2]])
                eye_region_squeezed = cv2.warpAffine(eye_region, M, (w, eye_region_h))
                
                # 替换原始区域
                img[eye_region_y:eye_region_y+eye_region_h, :, :] = eye_region_squeezed
        
        # 应用其他效果
        if "blur" in animations and animations["blur"]:
            blur_amount = animations.get("blur_amount", 3)
            img = cv2.GaussianBlur(img, (blur_amount*2+1, blur_amount*2+1), 0)
        
        if "zoom" in animations and animations["zoom"]:
            zoom_factor = animations.get("zoom_factor", 1.1)
            h, w = img.shape[:2]
            center_x, center_y = w // 2, h // 2
            
            # 计算变换矩阵
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            img = cv2.warpAffine(img, M, (w, h))
        
        return img
    
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
        if self.avatar_image is None:
            raise RuntimeError("尚未加载虚拟形象")
        
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # 获取输出参数
            fps = kwargs.get("fps", 30)
            width = kwargs.get("width", self.avatar_info["width"])
            height = kwargs.get("height", self.avatar_info["height"])
            
            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # 渲染每一帧
            for frame_idx in range(start_frame, end_frame + 1):
                frame = self.render_frame(frame_idx, **kwargs)
                
                # 转换为BGR格式（去除alpha通道）
                if frame.shape[2] == 4:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                else:
                    frame_bgr = frame
                
                video_writer.write(frame_bgr)
            
            video_writer.release()
            
            self.logger.info(f"渲染序列完成: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"渲染序列时出错: {str(e)}")
            raise
    
    def animate(self, animation_type: str, **kwargs) -> bool:
        """
        应用动画
        
        Args:
            animation_type: 动画类型
            **kwargs: 动画参数
            
        Returns:
            是否成功
        """
        if animation_type not in self.supported_features["animations"]:
            self.logger.error(f"不支持的动画类型: {animation_type}")
            return False
        
        try:
            # 更新动画状态
            self.animation_state[animation_type] = True
            self.animation_state.update(kwargs)
            
            self.logger.info(f"已应用动画: {animation_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"应用动画时出错: {str(e)}")
            return False
    
    def get_avatar_info(self) -> Dict[str, Any]:
        """
        获取虚拟形象信息
        
        Returns:
            虚拟形象信息
        """
        return self.avatar_info
    
    def get_supported_features(self) -> Dict[str, Any]:
        """
        获取支持的特性
        
        Returns:
            特性信息
        """
        return self.supported_features
    
    def cleanup(self) -> None:
        """
        清理资源
        """
        import shutil
        
        try:
            # 清除帧缓存
            self.frame_cache.clear()
            
            # 清除临时目录
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"已清理临时目录: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"清理资源时出错: {str(e)}")
    
    def __del__(self):
        """析构函数，确保清理资源"""
        self.cleanup() 