from shutil import which
import subprocess
import os

from ..exceptions import MissingLibraryError, InvalidVideoInput


def process(command):
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return (
        (process.stdout or b'').decode("utf-8"),
        (process.stderr or b'').decode("utf-8")
    )


def check_bin(bin):
    if which(bin) is None:
        raise MissingLibraryError
    return bin


class ffprobeCmdBuilder():

    def __init__(
        self,
        input,
        bin='ffprobe'
    ):
        self.input = input
        self.bin = check_bin(bin)

    @property
    def ffprobe(self):
        return f"{self.bin} -v error -select_streams v:0 -of csv=s=,:p=0"

    @property
    def resolution(self):
        return f"{self.ffprobe} -show_entries stream=width,height {self.input}"

    @property
    def video_bitrate(self):
        return f"{self.ffprobe} -show_entries stream=bit_rate {self.input}"

    @property
    def audio_bitrate(self):
        return f"{self.ffprobe} -select_streams a:0 -show_entries stream=bit_rate {self.input}"

    @property
    def duration(self):
        return f"{self.ffprobe} -show_entries stream=duration {self.input}"


class ffmpegCmdBuilder():

    def __init__(
        self,
        input=None,
        bin=None,
        mute=None,
        scale=None,
        bitrate=None,
    ):
        self.input = input
        self.bin = check_bin(bin)
        self.mute = mute
        self.scale = scale
        self.bitrate = bitrate

    @property
    def ffmpeg(self):
        return f"{self.bin} -i {self.input} -q:v 0"

    @property
    def mutefilter(self):
        return '-an' if self.mute else ''

    @property
    def scalefilter(self):
        return f'-vf scale={self.scale[0]}:{self.scale[1]}' if self.scale else ''

    @property
    def bitratefilter(self):
        return f'-maxrate:v {self.bitrate}' if self.bitrate else ''

    @property
    def pipestdout(self):
        return '-f null /dev/null 2>&1'

    @property
    def integrity(self):
        return f'{self.ffmpeg} -v error {self.pipestdout}'

    @property
    def volumedetect(self):
        return f"{self.ffmpeg} -af 'volumedetect' {self.pipestdout}"

    def export(self, output):
        return f'{self.ffmpeg} {self.mutefilter} {self.scalefilter} {self.bitratefilter} {output}'


class ffmpegProbeVideoInfoAdapter():

    def __init__(self, input=None, ffmpeg_bin='ffmpeg', ffprobe_bin='ffprobe'):
        self.input = input
        self.ffprobe = ffprobeCmdBuilder(input=input, bin=ffprobe_bin)
        self.ffmpeg = ffmpegCmdBuilder(input=input, bin=ffmpeg_bin)

    def check_video_integrity(self, input):
        trace, error = process(self.ffmpeg.integrity)
        if 'Invalid data' in trace or 'No such file or directory' in trace:
            raise InvalidVideoInput(trace)

    def volumedetect(self):
        volumetrace, error = process(self.ffmpeg.volumedetect)
        return 'Parsed_volumedetect' not in volumetrace

    def getResolution(self):
        resolution, error = process(self.ffprobe.resolution)
        return map(int, resolution.split(','))

    def getVideoBitrate(self):
        bitrate, error = process(self.ffprobe.video_bitrate)
        return int(bitrate) if bitrate else 0

    def getAudioBitrate(self):
        bitrate, error = process(self.ffprobe.audio_bitrate)
        return int(bitrate) if bitrate else 0

    def getDuration(self):
        duration, error = process(self.ffprobe.duration)
        duration = duration.replace('\n', '')
        return float(duration) * 1000

    def getSize(self):
        return os.path.getsize(self.input)


class ffmpegVideoCompressorAdapter():

    def __init__(
        self,
        input=None,
        bin_ffmpeg='ffmpeg',
        bin_ffprobe='ffprobe',
        mute=None,
        scale=None,
        bitrate=None,
    ):
        self._bin_ffmpeg = bin_ffmpeg
        self._bin_ffprobe = bin_ffprobe
        self._input = input
        self._mute = mute
        self._scale = scale
        self._bitrate = bitrate

    def export(self, output):
        ffmpeg = ffmpegCmdBuilder(**{
            'input': self._input,
            'bin': self._bin_ffmpeg,
            'mute': self._mute,
            'scale': self._scale,
            'bitrate': self._bitrate
        })
        process(ffmpeg.export(output))
