from video_compressor import functions 


def test_compute_slice_video_frames():

    assert list(functions.rangeSliceBySteps(0, 1, step=1)) == [(0, 1)]
    assert list(functions.rangeSliceBySteps(0, 2, step=1)) == [(0, 1), (1, 1)]
    assert list(functions.rangeSliceBySteps(0, 3, step=1)) == [(0, 1), (1, 1), (2, 1)]

    assert list(functions.rangeSliceBySteps(0, 1, step=2)) == [(0, 1)]
    assert list(functions.rangeSliceBySteps(0, 8, step=2)) == [(0, 2), (2, 2), (4, 2), (6, 2)]
    assert list(functions.rangeSliceBySteps(0, 9, step=2)) == [(0, 2), (2, 2), (4, 2), (6, 2), (8, 1)]

    assert list(functions.rangeSliceBySteps(1, 1, step=1)) == []
    assert list(functions.rangeSliceBySteps(1, 3, step=1)) == [(1, 1), (2, 1)]
    assert list(functions.rangeSliceBySteps(3, 8, step=2)) == [(3, 2), (5, 2), (7, 1)]