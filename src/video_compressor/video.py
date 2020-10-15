import os
from video_compressor.adapters.ffmpeg import ffmpegVideoCompressorAdapter, ffmpegProbeVideoInfoAdapter
import video_compressor.functions as vfunctions

class VideoInfo():

    @classmethod
    def defaultInfoAdapter(cls):
        return ffmpegProbeVideoInfoAdapter

    def __init__(self, path, adapter=None, **options):
        self.path = path
        self.adapter = adapter or VideoInfo.defaultInfoAdapter()(input=path, **options)
        self.adapter.check_video_integrity(path)

    def volumedetect(self):
        return self.adapter.volumedetect()

    def getVideoBitrate(self):
        return self.adapter.getVideoBitrate()

    def getAudioBitrate(self):
        return self.adapter.getAudioBitrate()

    def getResolution(self):
        return self.adapter.getResolution()

    def getDurationInMicroseconds(self):
        return self.adapter.getDurationInMicroseconds()

    def getDurationInMilliseconds(self):
        microseconds = self.getDurationInMicroseconds()
        return round(microseconds/1000)

    def getDurationInSeconds(self):
        milliseconds = self.getDurationInMilliseconds()
        return round(milliseconds/1000)

    def getSize(self):
        return self.adapter.getSize()


class VideoInfoCollection():

    def __init__(self, videos=None):
        self._videos = [VideoInfo(video) for video in (videos or [])]

    def __len__(self):
        return len(self._videos)

    def append(self, video):
        self._videos.append(VideoInfo(video))

    def getDurationInMicroseconds(self):
        return sum(map(lambda s: s.getDurationInMicroseconds(), self._videos))


class VideoCompressor():

    @classmethod
    def defaultCompressorAdapter(cls):
        return ffmpegVideoCompressorAdapter

    def __init__(
        self,
        input=None,
        mute=None,
        scale=None,
        bitrate=None,
        crop_origin=None,
        crop_size=None,
        adapter=None
    ):
        self._input = input
        self._mute = mute
        self._scale = scale
        self._bitrate = bitrate
        self._crop_origin = crop_origin
        self._crop_size = crop_size

        self.VideoCompressorAdapter = adapter or VideoCompressor.defaultCompressorAdapter()

    @property
    def compressor_adapter(self):
        return self.VideoCompressorAdapter(
            input=self._input,
            mute=self._mute,
            scale=self._scale,
            bitrate=self._bitrate,
            crop_origin=self._crop_origin,
            crop_size=self._crop_size
        )

    @property
    def info(self):
        return VideoInfo(self._input)

    def options(self):
        return {
            'input': self._input,
            'mute': self._mute,
            'scale': self._scale,
            'bitrate': self._bitrate
        }

    def update(self, **updates):
        options = self.options()
        options.update(updates)
        video = VideoCompressor(**options)
        video.VideoCompressorAdapter = self.VideoCompressorAdapter
        return video

    def mute(self, mute):
        return self.update(mute=mute)

    def scale(self, *scale):
        return self.update(scale=scale)

    def bitrate(self, bitrate):
        return self.update(bitrate=bitrate)

    def crop(self, origin, size):
        return self.update(crop_origin=origin, crop_size=size)

    def export(self, output):
        return self.compressor_adapter.export(output)

    def compressToTargetSize(self, targetSize, output):
        length = self.info.getDurationInMilliseconds() / 1000
        total_bitrate = targetSize / (length + 1)
        audio_bitrate = self.info.getAudioBitrate()
        video_bitrate = total_bitrate - audio_bitrate
        self.bitrate(video_bitrate).export(output)

    def slice(self, output, stepInMilliseconds=1000):
        
        videos = VideoInfoCollection()
        filename, ext = os.path.splitext(output)
        durationInMilliseconds = self.info.getDurationInMilliseconds()

        steps = vfunctions.rangeSliceBySteps(
            0, 
            durationInMilliseconds, 
            stepInMilliseconds
        )

        for i, step in enumerate(steps):
            start, duration = step
            filename = f'{filename}-{i}{ext}'
            self.compressor_adapter.slice(filename, start, duration)
            videos.append(filename)

        return videos

