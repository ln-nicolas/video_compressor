from shutil import which
import subprocess

from ..exceptions import MissingLibraryError, InvalidVideoInput


def process(command):
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return (
        (process.stdout or b'').decode("utf-8"),
        (process.stderr or b'').decode("utf-8")
    )


class ffmpegCmdBuilder():

    def __init__(
        self,
        input=None,
        bin_ffmpeg=None,
        mute=None,
        scale=None,
        output=None
    ):
        self.input = input
        self.bin_ffmpeg = bin_ffmpeg
        self.mute = mute
        self.scale = scale
        self.output = output

    @property
    def ffmpeg(self):
        return f"{self.bin_ffmpeg} -i {self.input} "

    @property
    def mutefilter(self):
        return '-an' if self.mute else ''

    @property
    def scalefilter(self):
        return f'-vf scale={self.scale[0]}:{self.scale[1]}' if self.scale else ''

    @property
    def pipestdout(self):
        return '-f null /dev/null 2>&1'

    @property
    def integrity(self):
        return f'{self.ffmpeg} -v error {self.pipestdout}'

    @property
    def export(self):
        return f'{self.ffmpeg} {self.mutefilter} {self.scalefilter} {self.output}'

    @property
    def volumedetect(self):
        return f"{self.ffmpeg} -af 'volumedetect' {self.pipestdout}"

    @property
    def resolution(self):
        return f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {self.input}"


class ffmpegAdapter():

    def __init__(
        self,
        input=None,
        bin_ffmpeg='ffmpeg',
        mute=None,
        scale=None,
        output=None
    ):
        self._bin_ffmpeg = bin_ffmpeg
        self._input = input
        self._mute = mute
        self._scale = scale
        self._output = output
        self.cmd = ffmpegCmdBuilder(**self.options())

        self._check_bin_validity(bin_ffmpeg)
        self._check_input_integrity(input)

    def options(self):
        return {
            'input': self._input,
            'bin_ffmpeg': self._bin_ffmpeg,
            'mute': self._mute,
            'scale': self._scale,
            'output': self._output
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

    def _check_bin_validity(self, bin):
        if which(bin) is None:
            raise MissingLibraryError

    def _check_input_integrity(self, input):
        trace, error = process(self.cmd.integrity)
        if 'Invalid data' in trace or 'No such file or directory' in trace:
            raise InvalidVideoInput(trace)

    def export(self, output):
        process(self.output(output).cmd.export)

    def volumedetect(self):
        volumetrace, error = process(self.cmd.volumedetect)
        return 'Parsed_volumedetect' not in volumetrace

    def resolution(self):
        resolution, error = process(self.cmd.resolution)
        return map(int, resolution.split('x'))
