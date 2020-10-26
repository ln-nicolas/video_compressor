# -*- coding: utf-8 -*-

import pytest
import os
import shutil

from video_compressor.exceptions import MissingLibraryError, InvalidVideoInput
import video_compressor as vp

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


def VideoInfo(input, **options):
    return vp.VideoInfo(
        input,
        mp4info_bin='/Users/nicolaslenselle/Downloads/Bento4-SDK-1-6-0-637.universal-apple-macosx/bin/mp4info',
        **options
    )

def VideoCompressor(input, **options):
    return vp.VideoCompressor(
        input,
        mp4info_bin='/Users/nicolaslenselle/Downloads/Bento4-SDK-1-6-0-637.universal-apple-macosx/bin/mp4info',
        mp4fragment_bin='/Users/nicolaslenselle/Downloads/Bento4-SDK-1-6-0-637.universal-apple-macosx/bin/mp4fragment',
        **options
    )

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
    assert VideoInfo('./tests/sample.mp4').volumedetect() is True
    assert VideoInfo('./tests/mute-sample.mp4').volumedetect() is False


def test_getVideoBitrate():
    assert VideoInfo('./tests/sample.mp4').getVideoBitrate() == 2200634


def test_getAudioBitrate():
    assert VideoInfo('./tests/sample.mp4').getAudioBitrate() == 133274


def test_get_video_resolution():
    video = VideoInfo('./tests/sample.mp4')
    w, h = video.getResolution()
    assert h == 540
    assert w == 960


def test_get_video_fps():
    video = VideoInfo('./tests/sample.mp4')
    fps = video.getFramePerSeconds()
    assert fps == 30

def test_get_video_duration_():
    video = VideoInfo('./tests/sample.mp4')
    d = video.getDurationInMicroseconds()
    assert d == 4_871_533

def test_get_video_duration_in_seconds():
    video = VideoInfo('./tests/sample.mp4')
    d = video.getDurationInSeconds()
    assert d == 5

def test_get_video_size():
    video = VideoInfo('./tests/sample.mp4')
    s = video.getSize()
    assert s == 1507453

def test_check_if_video_fragmentation(temp):
    video = VideoInfo('./tests/sample.mp4')
    fragmented = video.isFragmented()
    assert fragmented is False

def test_mute_a_video(temp):
    video = VideoCompressor(input='./tests/sample.mp4')

    sample_copy = temp(filename='sample-copy.mp4')
    sample_muted = temp(filename='sample-muted.mp4')

    video.export(sample_copy)
    video.mute(True).export(sample_muted)

    assert VideoInfo(sample_copy).volumedetect() is True
    assert VideoInfo(sample_muted).volumedetect() is False


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

def test_reduce_video_fps(temp):

    sample24fps = temp(filename='sample-24fps.mp4')
    video = VideoCompressor(input='./tests/sample.mp4')
    video.fps(24).export(sample24fps)

    fps = VideoInfo(sample24fps).getFramePerSeconds()
    assert fps == 24


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
    video.bitrate(1_000_000).export(sample1Mbs)

    assert VideoInfo(sample1Mbs).getVideoBitrate() < 1_000_000


def test_crop_video(temp):

    sampleCrop = temp(filename='sample-crop.mp4')
    video = VideoCompressor(input='./tests/sample.mp4')
    video.crop(origin=(10, 10), size=(100, 200)).export(sampleCrop)

    w, h = VideoInfo(sampleCrop).getResolution()
    assert w == 100
    assert h == 200

def test_combine_filter_crop_fps_bitrate(temp):

    Crop24fps1kBitrate = temp(filename='sample-crop-24ps-1kbitrate.mp4')
    video = VideoCompressor(input='./tests/sample.mp4')
    
    (video
        .crop(origin=(10, 10), size=(100, 200))
        .fps(24)
        .bitrate('2M')
        .mute(True)
        .export(Crop24fps1kBitrate)
    )

    info = VideoInfo(Crop24fps1kBitrate)
    w, h = video.info.getResolution()
    fps = video.info.getFramePerSeconds()
    
    assert list(info.getResolution()) == [100, 200]
    assert info.getFramePerSeconds() == 24
    assert info.getVideoBitrate() < 2_000_000

def test_combine_filter_scale_fps_bitrate_mute(temp):

    Crop24fps1kBitrate = temp(filename='sample-crop-24ps-1kbitrate.mp4')
    video = VideoCompressor(input='./tests/sample.mp4')
    
    (video
        .scale(640)
        .fps(24)
        .bitrate(1_000_000)
        .mute(True)
        .export(Crop24fps1kBitrate)
    )

    info = VideoInfo(Crop24fps1kBitrate)
    w, h = video.info.getResolution()
    fps = video.info.getFramePerSeconds()
    
    assert list(info.getResolution())[0] == 640
    assert info.getFramePerSeconds() == 24
    assert info.getVideoBitrate() < 1_000_000
    assert info.volumedetect() is False


def test_crop_video_checking_pixel(temp):
    # Test to compare pixel value from original video and crop video
    pass


def test_slice_video_by_1_seconds(temp):
    
    video = VideoCompressor(input='./tests/sample.mp4')

    slices = video.slice(temp('sample-slice.mp4'), stepInMilliseconds=1000)
    assert slices.getDurationInMicroseconds() == video.info.getDurationInMicroseconds()

    slices = video.slice(temp('sample-slice025.mp4'), stepInMilliseconds=2000)
    assert slices.getDurationInMicroseconds() == video.info.getDurationInMicroseconds()

def test_export_video_collection(temp):

    settings = [
        {'codec_preset': 'h264WebVBR', 'scale':[480, -1], 'bitrate': 200_000, 'fps': 24, 'suffix':'@sm'},
        {'codec_preset': 'h264WebVBR', 'scale':[480, -1], 'bitrate': 200_000, 'fps': 24, 'quality':'low', 'suffix':'@sm+low'},
        {'scale':[640, -1], 'bitrate': 1_000_000, 'fps': 24, 'suffix':'@md'},
        {'scale':[960, -1], 'bitrate': 2_000_000, 'fps': 24, 'suffix':'@lg'},
        {'scale':[1280, -1], 'bitrate': 3_000_000, 'fps': 24, 'suffix':'@xl'},
    ]

    video = VideoCompressor('./tests/sample.mp4')
    list(video.exportCollection(temp('sample.mp4'), settings))

    for setting in settings:
        suffix = setting['suffix']
        export = VideoInfo(temp(f'sample{suffix}.mp4'))
        assert list(export.getResolution())[0] == setting['scale'][0]
        assert export.getFramePerSeconds() == setting['fps']
        assert export.getVideoBitrate() < setting['bitrate']

    assert VideoInfo(temp(f'sample@sm+low.mp4')).getSize() < VideoInfo(temp(f'sample@sm.mp4')).getSize()


def test_hs264_webpreset(temp):

    h264WebPreset = temp('webh264.mp4')
    video = VideoCompressor('./tests/sample.mp4')
    video.bitrate('1M').codecPreset('h264WebVBR').export(h264WebPreset)

    assert VideoInfo(h264WebPreset).getSize() < video.info.getSize()


def test_export_video_with_height_not_divisable_by_two(temp):

    video = VideoCompressor(input='./tests/sample.mp4')

    w, h = video.info.getResolution()
    video.crop(origin=(0, 0), size=(w, h-1)).export(temp('video-crop.mp4'))

    videoCrop = VideoCompressor(input=temp('video-crop.mp4'))
    videoCrop.scale(480, -1).export(temp('video-crop2.mp4'))
    

def test_fragment_a_video(temp):

    video = VideoCompressor('./tests/sample.mp4')
    assert video.info.isFragmented() is False

    sample_fragmented = temp(filename='sample-fragment.mp4')

    video.fragment(sample_fragmented)
    assert VideoInfo(sample_fragmented).isFragmented() is True

# targetSize=$(( 25 * 1000 * 1000 * 8 )) # 25MB in bits
# length=`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4`
# length_round_up=$(( ${length%.*} + 1 ))
# total_bitrate=$(( $targetSize / $length_round_up ))
# audio_bitrate=$(( 128 * 1000 )) # 128k bit rate
# video_bitrate=$(( $total_bitrate - $audio_bitrate ))
# ffmpeg -i input.mp4 -b:v $video_bitrate -maxrate:v $video_bitrate
# -bufsize:v $(( $targetSize / 20 )) -b:a $audio_bitrate output.mp4
