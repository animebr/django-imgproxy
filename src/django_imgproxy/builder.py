__all__ = ["imgproxy"]

import base64
import hashlib
import hmac
import urllib.parse

from django_imgproxy import settings


def imgproxy(
    source_url: str,
    extension: str | None = None,
    b64_filename: str | None = None,
    **kwargs,
) -> str:
    source_url = settings.IMGPROXY_SOURCE_URL_PREFIX + source_url
    if settings.IMGPROXY_BASE64_ENCODE_SOURCE_URL:
        source_url = base64.urlsafe_b64encode(source_url.encode()).rstrip(b"=").decode()

        if b64_filename:
            source_url += "/" + urllib.parse.quote(b64_filename, safe="")
        elif extension:
            source_url += "." + extension
    else:
        source_url = urllib.parse.quote(
            source_url,
            safe=settings.IMGPROXY_PERCENT_ENCODE_SOURCE_URL_SAFE_CHARACTERS,
        )
        if extension:
            source_url += "@" + extension
        source_url = "plain/" + source_url

    processing_options = []
    if settings.IMGPROXY_ONLY_PRESETS:
        if presets := kwargs.get("preset", kwargs.get("pr")):
            processing_options.append(
                presets if isinstance(presets, str) else str(presets)
            )
    else:
        for option, arguments in kwargs.items():
            if option in settings.IMGPROXY_PERCENT_ENCODED_PROCESSING_OPTIONS:
                arguments = urllib.parse.quote(arguments, safe="")

            processing_options.append(
                "%s%s%s" % (option, settings.IMGPROXY_ARGUMENTS_SEPARATOR, arguments)
            )

    path = "/%s/%s" % ("/".join(processing_options), source_url)

    if settings.IMGPROXY_SIGN_URL:
        digest = hmac.digest(
            key=settings.IMGPROXY_KEY,
            msg=settings.IMGPROXY_SALT + path.encode(),
            digest=hashlib.sha256,
        )
        signature = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    else:
        signature = settings.IMGPROXY_NO_SIGNATURE_SEGMENT

    image_url = "%s/%s%s" % (settings.IMGPROXY_BASE_URL, signature, path)
    return image_url
