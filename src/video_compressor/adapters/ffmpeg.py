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


class ffprobeCmdBuilder():

    def __init__(
        self,
        input,
        **options
    ):
        self.input = input

    @property
    def ffprobe(self):
        return "ffprobe -v error -select_streams v:0 -of csv=s=,:p=0"

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
        bin_ffmpeg=None,
        mute=None,
        scale=None,
        bitrate=None,
        output=None,
        **options
    ):
        self.input = input
        self.bin_ffmpeg = bin_ffmpeg
        self.mute = mute
        self.scale = scale
        self.bitrate = bitrate
        self.output = output

    @property
    def ffmpeg(self):
        return f"{self.bin_ffmpeg} -i {self.input} -q:v 0"

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
    def export(self):
        return f'{self.ffmpeg} {self.mutefilter} {self.scalefilter} {self.bitratefilter} {self.output}'

    @property
    def volumedetect(self):
        return f"{self.ffmpeg} -af 'volumedetect' {self.pipestdout}"


class ffmpegAdapter():

    def __init__(
        self,
        input=None,
        bin_ffmpeg='ffmpeg',
        mute=None,
        scale=None,
        bitrate=None,
        output=None
    ):
        self._bin_ffmpeg = bin_ffmpeg
        self._input = input
        self._mute = mute
        self._scale = scale
        self._bitrate = bitrate
        self._output = output

        self.ffmpeg = ffmpegCmdBuilder(**self.options())
        self.ffprobe = ffprobeCmdBuilder(**self.options())

        self._check_bin_validity(bin_ffmpeg)
        self._check_input_integrity(input)

    def options(self):
        return {
            'input': self._input,
            'bin_ffmpeg': self._bin_ffmpeg,
            'mute': self._mute,
            'scale': self._scale,
            'output': self._output,
            'bitrate': self._bitrate
        }

    def update(self, **updates):
        options = self.options()
        options.update(updates)
        return ffmpegAdapter(**options)

    def bin_ffmpeg(self, bin_ffmpeg):
        self._check_bin_validity(bin_ffmpeg)
        return self.update(bin_ffmpeg=bin_ffmpeg)

    def input(self, input):
        return self.update(input=input)

    def output(self, output):
        return self.update(output=output)

    def mute(self, mute):
        return self.update(mute=mute)

    def scale(self, *scale):
        return self.update(scale=scale)

    def bitrate(self, bitrate):
        return self.update(bitrate=bitrate)

    def _check_bin_validity(self, bin):
        if which(bin) is None:
            raise MissingLibraryError

    def _check_input_integrity(self, input):
        trace, error = process(self.ffmpeg.integrity)
        if 'Invalid data' in trace or 'No such file or directory' in trace:
            raise InvalidVideoInput(trace)

    def export(self, output):
        process(self.output(output).ffmpeg.export)

    def volumedetect(self):
        volumetrace, error = process(self.ffmpeg.volumedetect)
        return 'Parsed_volumedetect' not in volumetrace

    def get_resolution(self):
        resolution, error = process(self.ffprobe.resolution)
        return map(int, resolution.split(','))

    def get_video_bitrate(self):
        bitrate, error = process(self.ffprobe.video_bitrate)
        return int(bitrate) if bitrate else 0

    def get_audio_bitrate(self):
        bitrate, error = process(self.ffprobe.audio_bitrate)
        return int(bitrate) if bitrate else 0

    def get_duration(self):
        duration, error = process(self.ffprobe.duration)
        duration = duration.replace('\n', '')
        return float(duration) * 1000

    def get_size(self):
        return os.path.getsize(self._input)
