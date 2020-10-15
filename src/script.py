from video_compressor import VideoCompressor

input = VideoCompressor(input='/Users/nicolaslenselle/Downloads/pexel.mp4')
input.exportCollection('./pexel.mp4', input.WebSettings)
input.codecPreset('h264WebVBR').exportCollection('./withcodec.mp4', input.WebSettings)