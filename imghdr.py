"""Recognize image file formats based on their first few bytes."""

__all__ = ["what"]

tests = []


def what(filename, h=None):
    if h is None:
        with open(filename, 'rb') as f:
            h = f.read(32)
    for tf in tests:
        res = tf(h, f)
        if res:
            return res
    return None


# --- Individual format test functions ---

def test_rgb(h, f):
    if h.startswith(b'\x01\xda'):
        return 'rgb'

def test_gif(h, f):
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

def test_pbm(h, f):
    if len(h) >= 3 and \
       h[0] == ord('P') and h[1] in b'14' and h[2] in b' \t\n\r':
        return 'pbm'

def test_pgm(h, f):
    if len(h) >= 3 and \
       h[0] == ord('P') and h[1] in b'25' and h[2] in b' \t\n\r':
        return 'pgm'

def test_ppm(h, f):
    if len(h) >= 3 and \
       h[0] == ord('P') and h[1] in b'36' and h[2] in b' \t\n\r':
        return 'ppm'

def test_tiff(h, f):
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

def test_rast(h, f):
    if h[:4] == b'\x59\xA6\x6A\x95':
        return 'rast'

def test_xbm(h, f):
    if h[:2] == b'/*':
        return 'xbm'

def test_bmp(h, f):
    if h[:2] == b'BM':
        return 'bmp'

def test_png(h, f):
    if h[:8] == b'\211PNG\r\n\032\n':
        return 'png'

def test_jpeg(h, f):
    if h[0:2] == b'\377\330':
        return 'jpeg'

def test_exr(h, f):
    if h[:4] == b'\x76\x2f\x31\x01':
        return 'exr'

def test_webp(h, f):
    if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'


# --- Register tests in order ---
tests.extend([
    test_rgb,
    test_gif,
    test_pbm,
    test_pgm,
    test_ppm,
    test_tiff,
    test_rast,
    test_xbm,
    test_bmp,
    test_png,
    test_jpeg,
    test_exr,
    test_webp,
])
