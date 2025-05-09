#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import subprocess
import time
import tempfile
import threading
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

import cv2
import numpy as np
import ffmpeg

from .interface import StreamingInterface


class RTMPStreamer(StreamingInterface):
    """
    RTMP直播推流实现
    使用FFmpeg进行推流
    """
    
    def __init__(self):
        self.logger = logging.getLogger("RTMPStreamer")
        self.config = {}
        self.stream_url = None
        self.stream_key = None
        self.video_bitrate = "2500k"
        self.audio_bitrate = "128k"
        self.resolution = (1280, 720)  # 默认720p
        self.fps = 30
        
        self.streaming = False
        self.ffmpeg_process = None
        self.temp_dir = tempfile.mkdtemp(prefix="rtmp_streamer_")
        self.input_fifo_path = os.path.join(self.temp_dir, "input.fifo")
        
        # 线程相关
        self.stream_thread = None
        self.thread_stop_event = threading.Event()
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化RTMP推流
        
        Args:
            config: 配置参数
                - platform: 平台类型，默认为rtmp
                - url: RTMP服务器URL
                - key: 直播密钥
                - video_bitrate: 视频比特率
                - audio_bitrate: 音频比特率
                - resolution: 分辨率，如"720p", "1080p"
                - fps: 帧率
            
        Returns:
            初始化是否成功
        """
        try:
            self.config = config
            
            # 解析RTMP URL和密钥
            self.stream_url = config.get("url", "rtmp://localhost/live")
            self.stream_key = config.get("key", "stream")
            
            # 完整的RTMP地址
            full_url = f"{self.stream_url}/{self.stream_key}"
            
            # 设置比特率
            self.video_bitrate = config.get("video_bitrate", "2500k")
            self.audio_bitrate = config.get("audio_bitrate", "128k")
            
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
            
            # 检查ffmpeg是否可用
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
                self.logger.info("FFmpeg可用，初始化成功")
            except (subprocess.SubprocessError, FileNotFoundError):
                self.logger.error("FFmpeg不可用，请安装FFmpeg")
                return False
            
            # 创建FIFO管道
            if os.path.exists(self.input_fifo_path):
                os.unlink(self.input_fifo_path)
            os.mkfifo(self.input_fifo_path)
            
            self.logger.info(f"RTMP推流器初始化成功，推流地址: {full_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化RTMP推流器时出错: {str(e)}")
            return False
    
    def start_streaming(self) -> bool:
        """
        开始直播
        
        Returns:
            是否成功开始直播
        """
        if self.streaming:
            self.logger.warning("直播已经在进行中")
            return True
        
        try:
            # 完整的RTMP地址
            full_url = f"{self.stream_url}/{self.stream_key}"
            
            # 构建FFmpeg命令
            cmd = [
                "ffmpeg",
                "-y",                             # 覆盖输出文件
                "-f", "rawvideo",                 # 输入格式
                "-vcodec", "rawvideo",            # 输入视频编解码器
                "-pix_fmt", "bgr24",              # 像素格式
                "-s", f"{self.resolution[0]}x{self.resolution[1]}",  # 分辨率
                "-r", str(self.fps),              # 帧率
                "-i", "-",                        # 从标准输入读取
                "-c:v", "libx264",                # 输出视频编解码器
                "-pix_fmt", "yuv420p",            # 输出像素格式
                "-preset", "veryfast",            # 编码速度
                "-tune", "zerolatency",           # 零延迟
                "-b:v", self.video_bitrate,       # 视频比特率
                "-maxrate", self.video_bitrate,   # 最大比特率
                "-bufsize", "6M",                 # 缓冲区大小
                "-g", str(self.fps * 2),          # GOP大小
                "-f", "flv",                      # 输出格式
                full_url                          # 输出URL
            ]
            
            # 启动FFmpeg进程
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            
            # 设置直播状态
            self.streaming = True
            self.thread_stop_event.clear()
            
            self.logger.info(f"开始RTMP直播: {full_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"开始直播时出错: {str(e)}")
            return False
    
    def stop_streaming(self) -> bool:
        """
        停止直播
        
        Returns:
            是否成功停止直播
        """
        if not self.streaming:
            self.logger.warning("直播未在进行")
            return True
        
        try:
            # 设置线程停止事件
            self.thread_stop_event.set()
            
            # 等待线程结束
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=5)
            
            # 终止FFmpeg进程
            if self.ffmpeg_process:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.wait(timeout=5)
                self.ffmpeg_process = None
            
            # 设置直播状态
            self.streaming = False
            
            self.logger.info("已停止RTMP直播")
            return True
            
        except Exception as e:
            self.logger.error(f"停止直播时出错: {str(e)}")
            return False
    
    def is_streaming(self) -> bool:
        """
        检查是否正在直播
        
        Returns:
            是否正在直播
        """
        return self.streaming
    
    def send_frame(self, frame: np.ndarray) -> bool:
        """
        发送视频帧
        
        Args:
            frame: BGR格式的视频帧
            
        Returns:
            是否成功发送
        """
        if not self.streaming or not self.ffmpeg_process:
            self.logger.error("直播未在进行，无法发送帧")
            return False
        
        try:
            # 确保帧大小正确
            if frame.shape[0] != self.resolution[1] or frame.shape[1] != self.resolution[0]:
                frame = cv2.resize(frame, self.resolution)
            
            # 确保帧格式正确(BGR)
            if frame.shape[2] == 4:  # RGBA格式
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            
            # 写入到FFMPEG进程
            self.ffmpeg_process.stdin.write(frame.tobytes())
            
            return True
            
        except Exception as e:
            self.logger.error(f"发送帧时出错: {str(e)}")
            # 如果出错，尝试重新开始直播
            self.stop_streaming()
            self.start_streaming()
            return False
    
    def send_audio(self, audio_data: Any) -> bool:
        """
        发送音频数据 (当前实现不支持直接发送音频)
        
        Args:
            audio_data: 音频数据
            
        Returns:
            是否成功发送
        """
        self.logger.warning("当前RTMP实现不支持直接发送音频，请使用send_video发送带音频的视频")
        return False
    
    def _stream_video_thread(self, video_path: str):
        """
        在线程中推流视频文件
        
        Args:
            video_path: 视频文件路径
        """
        try:
            # 完整的RTMP地址
            full_url = f"{self.stream_url}/{self.stream_key}"
            
            # 构建FFmpeg命令
            cmd = [
                "ffmpeg",
                "-re",                           # 实时模式
                "-i", video_path,                # 输入文件
                "-c:v", "libx264",               # 视频编解码器
                "-c:a", "aac",                   # 音频编解码器
                "-b:v", self.video_bitrate,      # 视频比特率
                "-b:a", self.audio_bitrate,      # 音频比特率
                "-pix_fmt", "yuv420p",           # 像素格式
                "-f", "flv",                     # 输出格式
                full_url                         # 输出URL
            ]
            
            # 启动FFmpeg进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待进程完成或被中断
            while not self.thread_stop_event.is_set():
                if process.poll() is not None:
                    break
                time.sleep(0.1)
            
            # 终止进程
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            
        except Exception as e:
            self.logger.error(f"流媒体线程出错: {str(e)}")
        finally:
            self.streaming = False
    
    def send_video(self, video_path: str) -> bool:
        """
        发送视频文件
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            是否成功发送
        """
        if not os.path.exists(video_path):
            self.logger.error(f"视频文件不存在: {video_path}")
            return False
        
        # 如果已经在流媒体中，先停止
        if self.streaming:
            self.stop_streaming()
        
        try:
            # 设置直播状态
            self.streaming = True
            self.thread_stop_event.clear()
            
            # 启动推流线程
            self.stream_thread = threading.Thread(
                target=self._stream_video_thread,
                args=(video_path,)
            )
            self.stream_thread.daemon = True
            self.stream_thread.start()
            
            self.logger.info(f"开始推流视频文件: {video_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送视频文件时出错: {str(e)}")
            self.streaming = False
            return False
    
    def get_stream_info(self) -> Dict[str, Any]:
        """
        获取流信息
        
        Returns:
            流信息字典
        """
        return {
            "url": self.stream_url,
            "key": self.stream_key,
            "resolution": f"{self.resolution[0]}x{self.resolution[1]}",
            "fps": self.fps,
            "video_bitrate": self.video_bitrate,
            "audio_bitrate": self.audio_bitrate,
            "streaming": self.streaming
        }
    
    def cleanup(self) -> None:
        """
        清理资源
        """
        import shutil
        
        # 停止直播
        if self.streaming:
            self.stop_streaming()
        
        # 清理FIFO
        if os.path.exists(self.input_fifo_path):
            os.unlink(self.input_fifo_path)
        
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        self.logger.info("已清理RTMP推流器资源")
    
    def __del__(self):
        """析构函数，确保清理资源"""
        self.cleanup() 