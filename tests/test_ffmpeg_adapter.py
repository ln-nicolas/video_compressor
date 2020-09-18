# -*- coding: utf-8 -*-

import pytest
import os
import shutil

from video_compressor.adapters.ffmpeg import ffmpegAdapter
from video_compressor.exceptions import MissingLibraryError

__author__ = "Lenselle Nicolas"
__copyright__ = "Lenselle Nicolas"
__license__ = "mit"

# remove sound on video
# check if video has sound or not


@pytest.fixture(scope="session")
def tempdir():
    return os.getcwd()+'/tmp/'


@pytest.fixture(scope="session")
def tempfile(tempdir):
    def path(filename=''):
        return tempdir+filename
    return path


@pytest.fixture(scope="session", autouse=True)
def beforeAll(tempdir):
    os.mkdir(tempdir)
    yield
    shutil.rmtree(tempdir)


def test_error_with_invalid_ffmpeg():
    with pytest.raises(MissingLibraryError):
        ffmpegAdapter(input='./sample.mp4', bin_ffmpeg='ffmpeg-custom-bin')
    with pytest.raises(MissingLibraryError):
        ffmpegAdapter(input='./sample.mp4').bin_ffmpeg('ffmpeg-custom-bin')


def test_error_with_invalid_input():
    pass


def test_error_with_invalid_ouput():
    pass


def test_error_with_invalid_mute_value():
    pass


def test_check_video_has_sound():
    assert ffmpegAdapter(input='./tests/sample.mp4').volumedetect() is False


def test_check_video_has_not_sound():
    assert ffmpegAdapter(input='./tests/mute-sample.mp4').volumedetect() is True


def test_mute_a_video(tempfile):
    video = ffmpegAdapter(input='./tests/sample.mp4')

    tmp01 = tempfile(filename='tmp1.mp4')
    tmp02 = tempfile(filename='tmp2.mp4')

    video.output(tmp01).export()
    video.output(tmp02).mute(True).export()

    assert ffmpegAdapter(input=tmp01).volumedetect() is False
    assert ffmpegAdapter(input=tmp02).volumedetect() is True


def test_get_video_size():
    video = ffmpegAdapter(input='./tests/sample.mp4')
    w, h = video.resolution()
    assert h == 540
    assert w == 960