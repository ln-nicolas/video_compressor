# -*- coding: utf-8 -*-

import pytest
import os
import shutil

from video_compressor.adapters.ffmpeg import ffmpegAdapter
from video_compressor.compressor import compressToTargetSize
from video_compressor.exceptions import MissingLibraryError, InvalidVideoInput

__author__ = "Lenselle Nicolas"
__copyright__ = "Lenselle Nicolas"
__license__ = "mit"

# remove sound on video
# check if video has sound or not


@pytest.fixture(scope="function")
def tempdir():
    return os.getcwd()+'/tmp/'


@pytest.fixture(scope="function")
def tempfile(tempdir):
    def path(filename=''):
        return tempdir+filename
    return path


@pytest.fixture(scope="function", autouse=True)
def beforeAll(tempdir):
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.mkdir(tempdir)
    yield
    shutil.rmtree(tempdir)


def test_error_with_invalid_ffmpeg():
    with pytest.raises(MissingLibraryError):
        ffmpegAdapter(input='./src/tests/sample.mp4', bin_ffmpeg='ffmpeg-custom-bin')
    with pytest.raises(MissingLibraryError):
        ffmpegAdapter(input='./src/tests/sample.mp4').bin_ffmpeg('ffmpeg-custom-bin')


def test_error_with_invalid_input():
    with pytest.raises(InvalidVideoInput):
        ffmpegAdapter(input='./src/tests/corrupted-sample.mp4')

    with pytest.raises(InvalidVideoInput):
        ffmpegAdapter(input='./src/tests/unexisting-sample.mp4')


def test_error_with_invalid_ouput():
    pass


def test_error_with_invalid_mute_value():
    pass


def test_error_with_invalid_scale_value():
    pass


def test_get_video_audio():
    assert ffmpegAdapter(input='./src/tests/sample.mp4').volumedetect() is False
    assert ffmpegAdapter(input='./src/tests/mute-sample.mp4').volumedetect() is True


def test_get_video_bitrate():
    assert ffmpegAdapter(input='./src/tests/sample.mp4').get_video_bitrate() == 2200634


def test_get_audio_bitrate():
    assert ffmpegAdapter(input='./src/tests/sample.mp4').get_audio_bitrate() == 133274


def test_get_video_resolution():
    video = ffmpegAdapter(input='./src/tests/sample.mp4')
    w, h = video.get_resolution()
    assert h == 540
    assert w == 960


def test_get_video_duration():
    video = ffmpegAdapter(input='./src/tests/sample.mp4')
    d = video.get_duration()
    assert d == 4871.533


def test_get_video_size():
    video = ffmpegAdapter(input='./src/tests/sample.mp4')
    s = video.get_size()
    assert s == 1507453


def test_mute_a_video(tempfile):
    video = ffmpegAdapter(input='./src/tests/sample.mp4')

    sample_copy = tempfile(filename='sample-copy.mp4')
    sample_muted = tempfile(filename='sample-muted.mp4')

    video.export(sample_copy)
    video.mute(True).export(sample_muted)

    assert ffmpegAdapter(input=sample_copy).volumedetect() is False
    assert ffmpegAdapter(input=sample_muted).volumedetect() is True


def test_scale_video(tempfile):

    sample54x96 = tempfile(filename='sample-54x96.mp4')

    video = ffmpegAdapter(input='./src/tests/sample.mp4')
    w, h = video.get_resolution()
    assert w == 960
    assert h == 540

    video.scale(96, 54).export(sample54x96)
    w, h = ffmpegAdapter(input=sample54x96).get_resolution()
    assert w == 96
    assert h == 54


def test_scale_video_keep_ratio(tempfile):

    sample640 = tempfile(filename='sample-54x96.mp4')

    video = ffmpegAdapter(input='./src/tests/sample.mp4')
    w1, h1 = video.get_resolution()

    video.scale(640, -1).export(sample640)
    w2, h2 = ffmpegAdapter(input=sample640).get_resolution()
    assert w2 // h2 == w1 // h1


def test_reduce_video_bitrate(tempfile):

    sample1Mbs = tempfile(filename='sample-1mbs.mp4')
    video = ffmpegAdapter(input='./src/tests/sample.mp4')

    video.bitrate(1000000).export(sample1Mbs)
    assert ffmpegAdapter(input=sample1Mbs).get_video_bitrate() < 1000000


def test_reduce_video_to_specific_size(tempfile):

    # 1 507 453 is ./src/tests/sample.mp4 original size

    maxSize = 0.5 * 1000 * 1000 * 8  # 0.5MB in bits
    sample500k = tempfile(filename='sample-500k.mp4')

    video = ffmpegAdapter(input='./src/tests/sample.mp4')
    compressToTargetSize(video, maxSize, sample500k)

    assert ffmpegAdapter(sample500k).get_size() < (maxSize / 8)

# target_size=$(( 25 * 1000 * 1000 * 8 )) # 25MB in bits
# length=`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4`
# length_round_up=$(( ${length%.*} + 1 ))
# total_bitrate=$(( $target_size / $length_round_up ))
# audio_bitrate=$(( 128 * 1000 )) # 128k bit rate
# video_bitrate=$(( $total_bitrate - $audio_bitrate ))
# ffmpeg -i input.mp4 -b:v $video_bitrate -maxrate:v $video_bitrate -bufsize:v $(( $target_size / 20 )) -b:a $audio_bitrate output.mp4
