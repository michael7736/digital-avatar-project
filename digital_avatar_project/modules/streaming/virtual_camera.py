#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import threading
import time
from typing import Dict, Any, Optional, List, Tuple

import cv2
import numpy as np

try:
    import pyvirtualcam
    VIRTUAL_CAMERA_AVAILABLE = True
except ImportError:
    VIRTUAL_CAMERA_AVAILABLE = False

from .interface import StreamingInterface


class VirtualCamera(StreamingInterface):
    """
    虚拟摄像头输出实现
    使用pyvirtualcam库将视频输出到虚拟摄像头
    """
    
    def __init__(self):
        self.logger = logging.getLogger("VirtualCamera")
        self.config = {}
        self.resolution = (1280, 720)  # 默认720p
        self.fps = 30
        
        self.streaming = False
        self.camera = None
        self.stream_thread = None
        self.thread_stop_event = threading.Event()
        self.frame_queue = []
        self.queue_lock = threading.Lock()
        self.current_frame = None
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化虚拟摄像头
        
        Args:
            config: 配置参数
                - resolution: 分辨率，如"720p", "1080p"
                - fps: 帧率
                - device: 虚拟摄像头设备名称（可选）
            
        Returns:
            初始化是否成功
        """
        if not VIRTUAL_CAMERA_AVAILABLE:
            self.logger.error("缺少pyvirtualcam库，请安装：pip install pyvirtualcam")
            return False
        
        try:
            self.config = config
            
            # 设置分辨率
            resolution = config.get("resolution", "720p")
            if resolution == "1080p":
                self.resolution = (1920, 1080)
            elif resolution == "720p":
                self.resolution = (1280, 720)
            elif resolution == "480p":
                self.resolution = (854, 480)
            elif resolution == "360p":
                self.resolution = (640, 360)
            else:
                self.logger.warning(f"未知的分辨率: {resolution}，使用默认值720p")
                self.resolution = (1280, 720)
            
            # 设置帧率
            self.fps = config.get("fps", 30)
            
            # 创建占位帧
            self.current_frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
            
            self.logger.info("虚拟摄像头初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化虚拟摄像头时出错: {str(e)}")
            return False
    
    def _stream_thread_func(self):
        """摄像头线程函数"""
        try:
            # 获取设备名称（如果指定）
            device = self.config.get("device", None)
            
            # 创建虚拟摄像头
            with pyvirtualcam.Camera(
                width=self.resolution[0],
                height=self.resolution[1],
                fps=self.fps,
                device=device,
                fmt=pyvirtualcam.PixelFormat.BGR,
            ) as cam:
                self.camera = cam
                self.logger.info(f"虚拟摄像头已启动: {cam.device}")
                
                # 主循环
                while not self.thread_stop_event.is_set():
                    # 获取当前帧
                    frame = self.current_frame.copy()
                    
                    # 确保格式正确（BGR）
                    if frame.shape[2] == 4:  # RGBA格式
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                    
                    # 确保大小正确
                    if frame.shape[0] != self.resolution[1] or frame.shape[1] != self.resolution[0]:
                        frame = cv2.resize(frame, (self.resolution[0], self.resolution[1]))
                    
                    # 发送到虚拟摄像头
                    cam.send(frame)
                    
                    # 控制帧率
                    cam.sleep_until_next_frame()
                
                self.camera = None
                self.logger.info("虚拟摄像头线程停止")
        
        except Exception as e:
            self.logger.error(f"虚拟摄像头线程出错: {str(e)}")
            self.streaming = False
    
    def start_streaming(self) -> bool:
        """
        开始推流
        
        Returns:
            是否成功开始推流
        """
        if self.streaming:
            self.logger.warning("虚拟摄像头已经在运行")
            return True
        
        try:
            # 清除停止标志
            self.thread_stop_event.clear()
            
            # 创建并启动线程
            self.stream_thread = threading.Thread(target=self._stream_thread_func)
            self.stream_thread.daemon = True
            self.stream_thread.start()
            
            # 设置状态
            self.streaming = True
            
            return True
            
        except Exception as e:
            self.logger.error(f"启动虚拟摄像头时出错: {str(e)}")
            return False
    
    def stop_streaming(self) -> bool:
        """
        停止推流
        
        Returns:
            是否成功停止推流
        """
        if not self.streaming:
            self.logger.warning("虚拟摄像头未在运行")
            return True
        
        try:
            # 设置停止标志
            self.thread_stop_event.set()
            
            # 等待线程结束
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=5)
            
            # 清空帧队列
            with self.queue_lock:
                self.frame_queue.clear()
            
            # 重置状态
            self.streaming = False
            
            self.logger.info("虚拟摄像头已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止虚拟摄像头时出错: {str(e)}")
            return False
    
    def is_streaming(self) -> bool:
        """
        检查是否正在推流
        
        Returns:
            是否正在推流
        """
        return self.streaming
    
    def send_frame(self, frame: np.ndarray) -> bool:
        """
        发送视频帧
        
        Args:
            frame: 视频帧
            
        Returns:
            是否成功发送
        """
        if not self.streaming:
            self.logger.warning("虚拟摄像头未启动，无法发送帧")
            return False
        
        try:
            # 更新当前帧
            self.current_frame = frame.copy()
            return True
            
        except Exception as e:
            self.logger.error(f"发送帧到虚拟摄像头时出错: {str(e)}")
            return False
    
    def send_audio(self, audio_data: Any) -> bool:
        """
        发送音频数据（虚拟摄像头不支持音频）
        
        Args:
            audio_data: 音频数据
            
        Returns:
            是否成功发送
        """
        self.logger.warning("虚拟摄像头不支持音频")
        return False
    
    def _video_thread(self, video_path: str):
        """
        视频文件播放线程
        
        Args:
            video_path: 视频文件路径
        """
        try:
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.logger.error(f"无法打开视频文件: {video_path}")
                self.streaming = False
                return
            
            # 获取视频FPS
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            if video_fps <= 0:
                video_fps = self.fps
            
            frame_time = 1.0 / video_fps
            
            # 播放视频
            while not self.thread_stop_event.is_set():
                start_time = time.time()
                
                ret, frame = cap.read()
                if not ret:
                    # 视频结束，循环播放
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # 更新当前帧
                self.current_frame = frame
                
                # 控制帧率
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # 释放资源
            cap.release()
            
        except Exception as e:
            self.logger.error(f"播放视频到虚拟摄像头时出错: {str(e)}")
        finally:
            self.streaming = False
    
    def send_video(self, video_path: str) -> bool:
        """
        发送视频文件到虚拟摄像头
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            是否成功发送
        """
        if not os.path.exists(video_path):
            self.logger.error(f"视频文件不存在: {video_path}")
            return False
        
        try:
            # 启动虚拟摄像头（如果尚未启动）
            if not self.streaming:
                if not self.start_streaming():
                    return False
            
            # 停止现有视频线程（如果有）
            if hasattr(self, 'video_thread') and self.video_thread and self.video_thread.is_alive():
                self.video_thread_stop.set()
                self.video_thread.join(timeout=2)
            
            # 创建停止事件和视频线程
            self.video_thread_stop = threading.Event()
            self.video_thread = threading.Thread(target=self._video_thread, args=(video_path,))
            self.video_thread.daemon = True
            self.video_thread.start()
            
            self.logger.info(f"开始播放视频到虚拟摄像头: {video_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送视频到虚拟摄像头时出错: {str(e)}")
            return False
    
    def get_stream_info(self) -> Dict[str, Any]:
        """
        获取流信息
        
        Returns:
            流信息字典
        """
        device = self.camera.device if self.camera else "未知"
        return {
            "type": "virtual_camera",
            "device": device,
            "resolution": f"{self.resolution[0]}x{self.resolution[1]}",
            "fps": self.fps,
            "streaming": self.streaming
        }
    
    def cleanup(self) -> None:
        """
        清理资源
        """
        # 停止视频线程
        if hasattr(self, 'video_thread_stop') and self.video_thread:
            self.video_thread_stop.set()
            if self.video_thread.is_alive():
                self.video_thread.join(timeout=2)
        
        # 停止摄像头
        self.stop_streaming()
        
        self.logger.info("虚拟摄像头资源已清理")
    
    def __del__(self):
        """析构函数，确保清理资源"""
        self.cleanup() 