from cogs.save_image import mime_type, upload_filename


def test_upload_filename_renames_default_discord_name():
    renamed = upload_filename("image0.png")
    assert renamed.endswith(".png") and renamed != "image0.png"
    assert upload_filename("cat.jpg") == "cat.jpg"
    assert upload_filename("image0") != "image0"


def test_mime_type_rejects_header_injection():
    assert mime_type("image/png") == "image/png"
    assert mime_type("text/plain; charset=utf-8") == "text/plain"
    assert mime_type(None) == "application/octet-stream"
    assert mime_type("image/png\r\nX-Evil: 1") == "application/octet-stream"
