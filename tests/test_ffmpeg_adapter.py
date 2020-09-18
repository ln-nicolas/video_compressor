# -*- coding: utf-8 -*-

import pytest
import os
import shutil

from video_compressor.adapters.ffmpeg import ffmpegAdapter
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
        ffmpegAdapter(input='./tests/sample.mp4', bin_ffmpeg='ffmpeg-custom-bin')
    with pytest.raises(MissingLibraryError):
        ffmpegAdapter(input='./tests/sample.mp4').bin_ffmpeg('ffmpeg-custom-bin')


def test_error_with_invalid_input():
    with pytest.raises(InvalidVideoInput):
        ffmpegAdapter(input='./tests/corrupted-sample.mp4')

    with pytest.raises(InvalidVideoInput):
        ffmpegAdapter(input='./tests/unexisting-sample.mp4')


def test_error_with_invalid_ouput():
    pass


def test_error_with_invalid_mute_value():
    pass


def test_error_with_invalid_scale_value():
    pass


def test_check_video_has_sound():
    assert ffmpegAdapter(input='./tests/sample.mp4').volumedetect() is False


def test_check_video_has_not_sound():
    assert ffmpegAdapter(input='./tests/mute-sample.mp4').volumedetect() is True


def test_mute_a_video(tempfile):
    video = ffmpegAdapter(input='./tests/sample.mp4')

    sample_copy = tempfile(filename='sample-copy.mp4')
    sample_muted = tempfile(filename='sample-muted.mp4')

    video.export(sample_copy)
    video.mute(True).export(sample_muted)

    assert ffmpegAdapter(input=sample_copy).volumedetect() is False
    assert ffmpegAdapter(input=sample_muted).volumedetect() is True


def test_get_video_size():
    video = ffmpegAdapter(input='./tests/sample.mp4')
    w, h = video.resolution()
    assert h == 540
    assert w == 960


def test_scale_video(tempfile):

    sample54x96 = tempfile(filename='sample-54x96.mp4')

    video = ffmpegAdapter(input='./tests/sample.mp4')
    w, h = video.resolution()
    assert w == 960
    assert h == 540

    video.scale(96, 54).export(sample54x96)
    w, h = ffmpegAdapter(input=sample54x96).resolution()
    assert w == 96
    assert h == 54


def test_scale_video_keep_ratio(tempfile):

    sample640 = tempfile(filename='sample-54x96.mp4')

    video = ffmpegAdapter(input='./tests/sample.mp4')
    w1, h1 = video.resolution()

    video.scale(640, -1).export(sample640)
    w2, h2 = ffmpegAdapter(input=sample640).resolution()
    assert w2 // h2 == w1 // h1


def test_get_video_bitrate():
    assert ffmpegAdapter(input='./tests/sample.mp4').bitrate() == 2200634