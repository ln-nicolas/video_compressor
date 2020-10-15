from video_compressor import VideoCompressor

input = VideoCompressor(input='../tests/sample.mp4')
input.exportCollection('./withoutcodec.mp4', input.WebSettings)
input.codecPreset('h264WebVBR').exportCollection('./withcodec.mp4', input.WebSettings)