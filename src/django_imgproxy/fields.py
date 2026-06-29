__all__ = ["ImgProxyImageFieldFile", "ImgProxyImageField"]

from datetime import timedelta

from django.db.models.fields.files import ImageField, ImageFieldFile
from django.utils import timezone

from django_imgproxy.builder import imgproxy
from django_imgproxy.settings import IMGPROXY_IMAGEFIELD_URL_TTL


class ImgProxyImageFieldFile(ImageFieldFile):
    @property
    def url(self) -> str:
        self._require_file()

        processing_options = {"raw": "true"}
        if ttl := IMGPROXY_IMAGEFIELD_URL_TTL:
            processing_options["expires"] = int(
                (timezone.now() + timedelta(seconds=ttl)).timestamp()
            )

        return imgproxy(self.name, **processing_options)


class ImgProxyImageField(ImageField):
    attr_class = ImgProxyImageFieldFile
