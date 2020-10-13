from video_compressor.adapters.ffmpeg import ffmpegVideoCompressorAdapter, ffmpegProbeVideoInfoAdapter


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

    def getDuration(self):
        return self.adapter.getDuration()

    def getSize(self):
        return self.adapter.getSize()


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
        adapter=None
    ):
        self._input = input
        self._mute = mute
        self._scale = scale
        self._bitrate = bitrate

        self.VideoCompressorAdapter = adapter or VideoCompressor.defaultCompressorAdapter()

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

    def export(self, output):
        adapter = self.VideoCompressorAdapter(
            input=self._input,
            mute=self._mute,
            scale=self._scale,
            bitrate=self._bitrate
        )
        return adapter.export(output)

    def compressToTargetSize(self, targetSize, output):
        info = VideoInfo(self._input)
        length = info.getDuration() / 1000
        total_bitrate = targetSize / (length+1)
        audio_bitrate = info.getAudioBitrate()
        video_bitrate = total_bitrate - audio_bitrate
        self.bitrate(video_bitrate).export(output)
