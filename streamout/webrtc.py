###############################################################################
#  Output — WebRTC 输出
###############################################################################

from streamout.base_output import BaseOutput
from registry import register
from utils.logger import logger
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from avatars.base_avatar import BaseAvatar


@register("streamout", "webrtc")
@register("streamout", "rtcpush")
class WebRTCOutput(BaseOutput):
    """WebRTC 输出模式 — 通过 aiortc 推送音视频"""

    def __init__(self, opt=None, parent: Optional['BaseAvatar'] = None, **kwargs):
        super().__init__(opt, parent)
        self._player = None

    def start(self) -> None:
        """WebRTC 输出由 rtc_manager 管理，此处无需额外启动"""
        pass

    def push_video_frame(self, frame) -> None:
        if self._player:
            self._player.push_video(frame)

    def push_audio_frame(self, frame, eventpoint=None) -> None:
        if self._player:
            self._player.push_audio(frame, eventpoint)



    def get_buffer_size(self) -> int:
        if self._player and hasattr(self._player, 'get_buffer_size'):
            return self._player.get_buffer_size()
        return 0

    def flush(self) -> None:
        """清空 WebRTC 发送队列 — 打断时立即丢弃所有待发送音视频帧"""
        if self._player:
            if hasattr(self._player, 'audio') and self._player.audio is not None:
                self._player.audio.drain()
            if hasattr(self._player, 'video') and self._player.video is not None:
                self._player.video.drain()

    def stop(self) -> None:
        pass
