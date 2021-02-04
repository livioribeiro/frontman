from frontman.provider import Provider


def test_provider_get_file_url():
    package, version, file = "$PACKAGE$", "$VERSION$", "$FILE$"

    cdnjs_url = Provider.CDNJS.get_file_url(package, version, file)
    jsdelivr_url = Provider.JSDELIVR.get_file_url(package, version, file)
    unpkg_url = Provider.UNPKG.get_file_url(package, version, file)

    assert (
        cdnjs_url == "https://cdnjs.cloudflare.com/ajax/libs/$PACKAGE$/$VERSION$/$FILE$"
    )
    assert jsdelivr_url == "https://cdn.jsdelivr.net/npm/$PACKAGE$@$VERSION$/$FILE$"
    assert unpkg_url == "https://unpkg.com/$PACKAGE$@$VERSION$/$FILE$"
