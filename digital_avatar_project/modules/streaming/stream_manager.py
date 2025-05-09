#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直播流管理模块
"""

import os
import logging
import subprocess
import threading
import time
import queue
from pathlib import Path

logger = logging.getLogger(__name__)

class StreamManager:
    """直播流管理器，负责将生成的内容推送到直播平台"""
    
    def __init__(self, config):
        """初始化直播流管理器
        
        Args:
            config (dict): 直播流配置
        """
        self.config = config
        self.platform = config.get("platform", "rtmp")
        self.stream_url = config.get("url", "rtmp://localhost/live")
        self.stream_key = config.get("key", "stream")
        self.video_bitrate = config.get("video_bitrate", "2500k")
        self.audio_bitrate = config.get("audio_bitrate", "128k")
        self.resolution = config.get("resolution", "720p")
        
        # 根据分辨率设置宽高
        self.width, self.height = self._parse_resolution(self.resolution)
        
        # 初始化直播状态和线程
        self.is_streaming = False
        self.stream_thread = None
        self.stream_process = None
        self.content_queue = queue.Queue()
        
        logger.info(f"直播流管理器初始化完成, 平台: {self.platform}")
    
    def _parse_resolution(self, resolution):
        """解析分辨率
        
        Args:
            resolution (str): 分辨率字符串，如"720p"、"1080p"或"1280x720"
        
        Returns:
            tuple: (宽度, 高度)
        """
        if resolution == "480p":
            return 854, 480
        elif resolution == "720p":
            return 1280, 720
        elif resolution == "1080p":
            return 1920, 1080
        elif "x" in resolution:
            parts = resolution.split("x")
            if len(parts) == 2:
                try:
                    width = int(parts[0])
                    height = int(parts[1])
                    return width, height
                except ValueError:
                    pass
        
        # 默认返回720p
        logger.warning(f"无法解析分辨率: {resolution}, 将使用720p")
        return 1280, 720
    
    def start(self):
        """启动直播流"""
        if self.is_streaming:
            logger.warning("直播流已经在运行中")
            return
        
        self.is_streaming = True
        self.stream_thread = threading.Thread(target=self._stream_worker)
        self.stream_thread.daemon = True
        self.stream_thread.start()
        
        logger.info("直播流已启动")
    
    def stop(self):
        """停止直播流"""
        if not self.is_streaming:
            logger.warning("直播流未运行")
            return
        
        self.is_streaming = False
        
        # 等待线程结束
        if self.stream_thread:
            self.stream_thread.join(timeout=5)
        
        # 终止流程
        if self.stream_process:
            self.stream_process.terminate()
            self.stream_process = None
        
        logger.info("直播流已停止")
    
    def push_content(self, video_file, audio_file=None):
        """将内容推送到直播流
        
        Args:
            video_file (str): 视频文件路径
            audio_file (str, optional): 音频文件路径，如果不指定则使用视频中的音频
        
        Returns:
            bool: 是否成功加入队列
        """
        if not Path(video_file).exists():
            logger.error(f"视频文件不存在: {video_file}")
            return False
        
        if audio_file and not Path(audio_file).exists():
            logger.warning(f"音频文件不存在: {audio_file}, 将使用视频中的音频")
            audio_file = None
        
        try:
            # 将内容加入队列
            self.content_queue.put((video_file, audio_file))
            logger.info(f"内容已加入推流队列: {video_file}")
            return True
        
        except Exception as e:
            logger.error(f"加入推流队列失败: {str(e)}")
            return False
    
    def _stream_worker(self):
        """直播流工作线程"""
        logger.info("直播流工作线程启动")
        
        while self.is_streaming:
            try:
                # 尝试从队列获取内容
                try:
                    video_file, audio_file = self.content_queue.get(timeout=1)
                    self._stream_content(video_file, audio_file)
                    self.content_queue.task_done()
                except queue.Empty:
                    # 队列为空，等待一段时间
                    time.sleep(0.1)
            
            except Exception as e:
                logger.error(f"直播流工作线程发生错误: {str(e)}")
                time.sleep(1)
        
        logger.info("直播流工作线程结束")
    
    def _stream_content(self, video_file, audio_file=None):
        """将内容推流到直播平台
        
        Args:
            video_file (str): 视频文件路径
            audio_file (str, optional): 音频文件路径，如果不指定则使用视频中的音频
        """
        try:
            if self.platform == "rtmp":
                self._stream_rtmp(video_file, audio_file)
            elif self.platform == "virtual_camera":
                self._stream_virtual_camera(video_file, audio_file)
            else:
                logger.warning(f"未知的直播平台: {self.platform}")
        
        except Exception as e:
            logger.error(f"推流内容失败: {str(e)}")
    
    def _stream_rtmp(self, video_file, audio_file=None):
        """将内容推流到RTMP服务器
        
        Args:
            video_file (str): 视频文件路径
            audio_file (str, optional): 音频文件路径，如果不指定则使用视频中的音频
        """
        # 构建完整的RTMP URL
        rtmp_url = f"{self.stream_url}/{self.stream_key}"
        
        # 构建FFmpeg命令
        cmd = [
            "ffmpeg",
            "-re",  # 实时模式
            "-i", video_file
        ]
        
        # 如果指定了音频文件，添加音频输入
        if audio_file:
            cmd.extend(["-i", audio_file])
        
        # 添加输出选项
        cmd.extend([
            "-c:v", "libx264",
            "-b:v", self.video_bitrate,
            "-c:a", "aac",
            "-b:a", self.audio_bitrate,
            "-s", f"{self.width}x{self.height}",
            "-f", "flv",
            rtmp_url
        ])
        
        logger.info(f"执行FFmpeg命令: {' '.join(cmd)}")
        
        # 终止之前的进程
        if self.stream_process:
            self.stream_process.terminate()
        
        # 启动新的流进程
        self.stream_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 读取输出，避免管道阻塞
        for line in self.stream_process.stderr:
            logger.debug(f"FFmpeg: {line.strip()}")
            if not self.is_streaming:
                break
        
        # 等待进程结束
        self.stream_process.wait()
        logger.info(f"FFmpeg进程已结束, 返回码: {self.stream_process.returncode}")
    
    def _stream_virtual_camera(self, video_file, audio_file=None):
        """将视频输出到虚拟摄像头
        
        Args:
            video_file (str): 视频文件路径
            audio_file (str, optional): 音频文件路径，如果不指定则使用视频中的音频
        """
        try:
            import pyvirtualcam
            import cv2
            from moviepy.editor import VideoFileClip
            
            # 加载视频
            video = VideoFileClip(video_file)
            fps = video.fps
            
            # 创建虚拟摄像头
            with pyvirtualcam.Camera(width=self.width, height=self.height, fps=fps) as cam:
                logger.info(f"虚拟摄像头已创建: {cam.device}")
                
                # 处理每一帧
                for frame in video.iter_frames(fps=fps):
                    if not self.is_streaming:
                        break
                    
                    # 调整帧大小
                    if frame.shape[0] != self.height or frame.shape[1] != self.width:
                        frame = cv2.resize(frame, (self.width, self.height))
                    
                    # 转换为BGR格式（如果需要）
                    if frame.shape[2] == 4:  # RGBA
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                    elif frame.shape[2] == 3:  # RGB
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # 发送帧到虚拟摄像头
                    cam.send(frame)
                    cam.sleep_until_next_frame()
                
                logger.info("视频已完全输出到虚拟摄像头")
        
        except ImportError:
            logger.error("未安装pyvirtualcam或moviepy包，请安装相应依赖")
        except Exception as e:
            logger.error(f"输出到虚拟摄像头失败: {str(e)}")
    
    def is_active(self):
        """检查直播流是否处于活动状态
        
        Returns:
            bool: 直播流是否活动
        """
        return self.is_streaming and (self.stream_thread is not None) and self.stream_thread.is_alive() 