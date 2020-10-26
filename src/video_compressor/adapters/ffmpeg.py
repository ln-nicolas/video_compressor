from shutil import which
import subprocess
import os
import json

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

    @property
    def fps(self):
        return f"{self.ffprobe} -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate {self.input}"



class ffmpegCmdBuilder():

    def __init__(
        self,
        input=None,
        bin=None,
        mute=None,
        scale=None,
        bitrate=None,
        crop_origin=None,
        crop_size=None,
        codec_preset=None,
        codec_pass=None,
        quality=None,
        fps=None
    ):
        self.input = input
        self.bin = check_bin(bin)
        self.mute = mute
        self.scale = scale
        self.bitrate = bitrate
        self.crop_origin = crop_origin
        self.crop_size = crop_size
        self.codec_preset = codec_preset
        self.codec_pass = codec_pass
        self.quality = quality
        self.fps = fps

    @property
    def ffmpeg(self):
        return f"{self.bin} -i {self.input}"

    @property
    def mutefilter(self):
        return '-an' if self.mute else ''

    @property
    def scalefilter(self):

        if not self.scale:
            return ""

        w, h = self.scale
        if w == -1:
            w = 'trunc(oh/a/2)*2'
        if h == -1:
            h = 'trunc(ow/a/2)*2'

        return f'scale={w}:{h}'

    @property
    def bitratefilter(self):
        return f'-b:v {self.bitrate}' if self.bitrate else ''

    @property
    def fpsfilter(self):
        return f'fps=fps={self.fps}' if self.fps else ''

    @property
    def cropfilter(self):
        if not self.crop_origin and not self.crop_size:
            return ""

        x, y = self.crop_origin
        w, h = self.crop_size 

        return f'crop={w}:{h}:{x}:{y}'

    @property
    def pipestdout(self):
        return '-f null /dev/null 2>&1'

    @property
    def integrity(self):
        return f'{self.ffmpeg} -v error {self.pipestdout}'

    @property
    def volumedetect(self):
        return f"{self.ffmpeg} -af 'volumedetect' {self.pipestdout}"

    @property
    def vfilters(self):
        filters = list(filter(lambda f: f != '', [
            self.cropfilter,
            self.fpsfilter,
            self.scalefilter
        ]))

        if len(filters) > 0:
            return '-vf "'+ ','.join(filters) + '"'
        else:
            return ""

    @property
    def filters(self):
        return f'{self.mutefilter} {self.bitratefilter} {self.vfilters}'

    @property
    def crf_quality(self):
        return ({
            'low': '-crf 35',
            'max': '-crf 0' 
        }).get(self.quality, '-crf 24')

    @property
    def codec(self):
        if self.codec_preset == 'h264WebVBR':
            return f"-c:v libx264 {self.crf_quality} -profile:v main -level 4.0"
        else:
            return ""

    def export(self, output):
        return f'{self.ffmpeg} {self.codec} {self.filters} {output}'

    def slice(self, output, start, duration):
        return f'{self.ffmpeg} {self.codec} {self.filters} -ss {start} -t {duration} {output}'


class mp4InfoCmdBuilder():

    def __init__(self, bin, input):
        self._bin = check_bin(bin)
        self._input = input

    @property
    def info(self):
        return f"{self._bin} --format json {self._input}"


class ffmpegProbeVideoInfoAdapter():

    def __init__(self, input=None, ffmpeg_bin='ffmpeg', ffprobe_bin='ffprobe', mp4info_bin='mp4info', **kwargs):
        self.input = input
        self.ffprobe = ffprobeCmdBuilder(input=input, bin=ffprobe_bin)
        self.ffmpeg = ffmpegCmdBuilder(input=input, bin=ffmpeg_bin)
        self.mp4Info = mp4InfoCmdBuilder(input=input, bin=mp4info_bin)

    def check_video_integrity(self, input):
        trace, error = process(self.ffmpeg.integrity)
        if 'Invalid data' in trace or 'No such file or directory' in trace:
            raise InvalidVideoInput(trace)

    def volumedetect(self):
        volumetrace, error = process(self.ffmpeg.volumedetect)
        return ('Parsed_volumedetect' in volumetrace)

    def getResolution(self):
        resolution, error = process(self.ffprobe.resolution)
        return map(int, resolution.split(','))

    def getVideoBitrate(self):
        bitrate, error = process(self.ffprobe.video_bitrate)
        return int(bitrate) if bitrate else 0

    def getAudioBitrate(self):
        bitrate, error = process(self.ffprobe.audio_bitrate)
        return int(bitrate) if bitrate else 0

    def getDurationInMicroseconds(self):
        duration, error = process(self.ffprobe.duration)
        duration = duration.replace('\n', '')
        return round(float(duration) * 1000 * 1000)

    def getSize(self):
        return os.path.getsize(self.input)

    def getFramePerSeconds(self):
        rate, error = process(self.ffprobe.fps)
        return round(eval(rate))

    def isFragmented(self):
        info, error = process(self.mp4Info.info)
        info = json.loads(info)
        return info['movie']['fragments']
class ffmpegVideoCompressorAdapter():

    def __init__(
        self,
        input=None,
        ffmpeg_bin='ffmpeg',
        ffprobe_bin='ffprobe',
        mp4info_bin='mp4info',
        mp4fragment_bin='mp4fragment',
        mute=None,
        scale=None,
        bitrate=None,
        crop_origin=None,
        crop_size=None,
        codec_preset=None,
        quality=None,
        fps=None,
    ):
        self._bin_ffmpeg = ffmpeg_bin
        self._bin_ffprobe = ffprobe_bin
        self._bin_mp4info = mp4info_bin
        self._bin_mp4fragment = mp4fragment_bin
        self._input = input
        self._mute = mute
        self._scale = scale
        self._bitrate = bitrate
        self._crop_origin = crop_origin
        self._crop_size = crop_size
        self._fps = fps
        self._codec_preset = codec_preset
        self._quality = quality

    @property
    def ffmpeg(self):
        return ffmpegCmdBuilder(**{
            'input': self._input,
            'bin': self._bin_ffmpeg,
            'mute': self._mute,
            'scale': self._scale,
            'bitrate': self._bitrate,
            'crop_origin': self._crop_origin,
            'crop_size': self._crop_size,
            'codec_preset': self._codec_preset,
            'quality': self._quality,
            'fps': self._fps
        })

    def export(self, output):
        process(self.ffmpeg.export(output))

    def slice(self, output, startInMillisecond, durationInMicroseconds):
        start_str = str(round(startInMillisecond / 1000, 3))
        duration_str = str(round(durationInMicroseconds / 1000, 3))
        process(self.ffmpeg.slice(output, start_str, duration_str))

    def fragment(self, output):
        check_bin(self._bin_mp4fragment)
        process(f'{self._bin_mp4fragment} {self._input} {output}')