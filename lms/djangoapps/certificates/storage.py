"""
Storage backend for certificates QR codes.
"""
from __future__ import absolute_import

from django.conf import settings
from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage
from storages.utils import setting


class CertificatesQRCodeS3Storage(S3BotoStorage):  # pylint: disable=abstract-method
    """
    S3 backend for course import and export OLX files.
    """

    def __init__(self):
        bucket = setting('CERTIFICATES_QR_CODE_BUCKET',
                         settings.AWS_STORAGE_BUCKET_NAME)
        super(CertificatesQRCodeS3Storage, self).__init__(bucket=bucket,
                                                          custom_domain=None,
                                                          querystring_auth=False,
                                                          acl='public-read')


# pylint: disable=invalid-name
certificates_qr_code_storage = get_storage_class(settings.CERTIFICATES_QR_CODE_STORAGE)()
