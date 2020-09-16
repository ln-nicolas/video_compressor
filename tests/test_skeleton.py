# -*- coding: utf-8 -*-

import pytest
from video_compressor.skeleton import fib

__author__ = "sne3ks"
__copyright__ = "sne3ks"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
