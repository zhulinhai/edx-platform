from datetime import datetime, timedelta

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import View

from botocore.signers import CloudFrontSigner


class SecureCloudFrontVideo(View):
    """
    """

    def get(self, request, *args, **kwargs):
        """
        """
        key = request.GET.get('key')

        if not key:
            raise Http404

        try:
            cloudfront_url = settings.CLOUDFRONT_URL
            cloudfront_id = settings.CLOUDFRONT_ID
        except AttributeError:
            raise Http404

        resource = '{}/{}'.format(cloudfront_url, key)

        expiration_date = _in_an_minute()

        cloudfront_signer = CloudFrontSigner(cloudfront_id, rsa_signer)
        redirect_url = cloudfront_signer.generate_presigned_url(resource, date_less_than=expiration_date)

        return redirect(redirect_url)


def rsa_signer(message):

    try:
        cloudfront_key = settings.CLOUDFRONT_PRIVATE_SIGNING_KEY
    except AttributeError:
        raise Http404

    private_key = serialization.load_pem_private_key(
        cloudfront_key,
        password=None,
        backend=default_backend()
    )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


def _in_an_minute():
    """
    """
    minute = timedelta(minutes=1)
    now = datetime.utcnow()
    return now + minute
