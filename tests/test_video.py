# -*- coding: utf-8 -*-

import pytest
import os
import shutil

from video_compressor.exceptions import MissingLibraryError, InvalidVideoInput
from video_compressor import VideoCompressor, VideoInfo

__author__ = "Lenselle Nicolas"
__copyright__ = "Lenselle Nicolas"
__license__ = "mit"

# remove sound on video
# check if video has sound or not


@pytest.fixture(scope="function")
def tempdir():
    return os.getcwd() + '/tmp/'


@pytest.fixture(scope="function")
def temp(tempdir):
    def path(filename=''):
        return tempdir + filename
    return path


@pytest.fixture(scope="function", autouse=True)
def beforeAll(tempdir):
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.mkdir(tempdir)
    yield
    shutil.rmtree(tempdir)


def test_error_with_invalid_ffmpeg():
    VideoInfo('./tests/sample.mp4', ffprobe_bin='ffprobe')
    with pytest.raises(MissingLibraryError):
        VideoInfo('./tests/sample.mp4', ffprobe_bin='ffprobe-custom-bin')


def test_error_with_invalid_input():

    with pytest.raises(InvalidVideoInput):
        VideoInfo('./tests/corrupted-sample.mp4')

    with pytest.raises(InvalidVideoInput):
        VideoInfo('./tests/unexisting-sample.mp4')


def test_error_with_invalid_ouput():
    pass


def test_error_with_invalid_mute_value():
    pass


def test_error_with_invalid_scale_value():
    pass


def test_get_video_audio():
    assert VideoInfo('./tests/sample.mp4').volumedetect() is False
    assert VideoInfo('./tests/mute-sample.mp4').volumedetect() is True


def test_getVideoBitrate():
    assert VideoInfo('./tests/sample.mp4').getVideoBitrate() == 2200634


def test_getAudioBitrate():
    assert VideoInfo('./tests/sample.mp4').getAudioBitrate() == 133274


def test_get_video_resolution():
    video = VideoInfo('./tests/sample.mp4')
    w, h = video.getResolution()
    assert h == 540
    assert w == 960


def test_get_video_duration_():
    video = VideoInfo('./tests/sample.mp4')
    d = video.getDurationInMilliseconds()
    assert d == 4871.533

def test_get_video_duration_in_seconds():
    video = VideoInfo('./tests/sample.mp4')
    d = video.getDurationInSeconds()
    assert d == 5

def test_get_video_size():
    video = VideoInfo('./tests/sample.mp4')
    s = video.getSize()
    assert s == 1507453


def test_mute_a_video(temp):
    video = VideoCompressor(input='./tests/sample.mp4')

    sample_copy = temp(filename='sample-copy.mp4')
    sample_muted = temp(filename='sample-muted.mp4')

    video.export(sample_copy)
    video.mute(True).export(sample_muted)

    assert VideoInfo(sample_copy).volumedetect() is False
    assert VideoInfo(sample_muted).volumedetect() is True


def test_scale_video(temp):

    sample54x96 = temp(filename='sample-54x96.mp4')

    w, h = VideoInfo('./tests/sample.mp4').getResolution()
    assert w == 960
    assert h == 540

    video = VideoCompressor(input='./tests/sample.mp4')
    video.scale(96, 54).export(sample54x96)
    w, h = VideoInfo(sample54x96).getResolution()
    assert w == 96
    assert h == 54


def test_scale_video_keep_ratio(temp):

    sample640 = temp(filename='sample-54x96.mp4')

    w1, h1 = VideoInfo('./tests/sample.mp4').getResolution()

    video = VideoCompressor(input='./tests/sample.mp4')
    video.scale(640, -1).export(sample640)
    w2, h2 = VideoInfo(sample640).getResolution()
    assert w2 // h2 == w1 // h1


def test_reduce_video_bitrate(temp):

    sample1Mbs = temp(filename='sample-1mbs.mp4')
    video = VideoCompressor(input='./tests/sample.mp4')
    video.bitrate(1000000).export(sample1Mbs)

    assert VideoInfo(sample1Mbs).getVideoBitrate() < 1000000


def test_crop_video(temp):

    sample1Mbs = temp(filename='sample-crop.mp4')
    video = VideoCompressor(input='./tests/sample.mp4')
    video.crop(origin=(10, 10), size=(100, 200)).export(sample1Mbs)

    w, h = VideoInfo(sample1Mbs).getResolution()
    assert w == 100
    assert h == 200

def test_crop_video_checking_pixel(temp):
    # Test to compare pixel value from original video and crop video
    pass


def test_slice_video_by_1_seconds(temp):
    
    video = VideoCompressor(input='./tests/sample.mp4')

    slices = video.slices(temp('sample-slice.mp4'), seconds=1)
    assert len(slices) == video.info.getDurationInSeconds()
    assert round(slices.getDurationInMilliseconds() * 100) == round(video.info.getDurationInMilliseconds() * 100)

    slices = video.slices(temp('sample-slice025.mp4'), seconds=2)
    assert len(slices) == video.info.getDurationInSeconds() // 2
    assert round(slices.getDurationInMilliseconds() * 100) == round(video.info.getDurationInMilliseconds() * 100)


def test_reduce_video_to_specific_size(temp):

    # 1 507 453 is ./tests/sample.mp4 original size

    maxSize = 0.5 * 1000 * 1000 * 8  # 0.5MB in bits
    sample500k = temp(filename='sample-500k.mp4')

    video = VideoCompressor(input='./tests/sample.mp4')
    video.compressToTargetSize(maxSize, sample500k)

    assert VideoInfo(sample500k).getSize() < (maxSize / 8)

# targetSize=$(( 25 * 1000 * 1000 * 8 )) # 25MB in bits
# length=`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4`
# length_round_up=$(( ${length%.*} + 1 ))
# total_bitrate=$(( $targetSize / $length_round_up ))
# audio_bitrate=$(( 128 * 1000 )) # 128k bit rate
# video_bitrate=$(( $total_bitrate - $audio_bitrate ))
# ffmpeg -i input.mp4 -b:v $video_bitrate -maxrate:v $video_bitrate
# -bufsize:v $(( $targetSize / 20 )) -b:a $audio_bitrate output.mp4
