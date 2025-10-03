def test_ocr_smoke():
    try:
        from modules.ocr import ocr_image_to_text
    except Exception:
        assert False, "ocr module import failed"
    # we don't have an image in CI; just assert callable
    assert callable(ocr_image_to_text)
