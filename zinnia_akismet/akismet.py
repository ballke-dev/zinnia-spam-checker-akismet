"""Akismet spam checker backend for Zinnia"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str

from zinnia.settings import PROTOCOL

from zinnia_akismet.api import APIKeyError
from zinnia_akismet.api import Akismet

if not getattr(settings, 'AKISMET_API_KEY', ''):
    raise ImproperlyConfigured('You have to set AKISMET_API_KEY')

AKISMET_API_KEY = settings.AKISMET_API_KEY


def backend(comment, content_object, request):
    """
    Akismet spam checker backend for Zinnia.
    """
    blog_url = '%s://%s/' % (PROTOCOL, Site.objects.get_current().domain)

    akismet = Akismet(key=AKISMET_API_KEY, blog_url=blog_url)

    if not akismet.verify_key():
        raise APIKeyError('Your Akismet API key is invalid.')

    akismet_data = {
        'user_ip': request.META.get('REMOTE_ADDR', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', 'unknown'),
        'permalink': content_object.get_absolute_url(),
        'comment_type': 'comment',
        'comment_author': smart_str(comment.name),
        'comment_author_email': smart_str(comment.email),
        'comment_author_url': smart_str(comment.url),
    }
    is_spam = akismet.comment_check(smart_str(comment.comment),
                                    data=akismet_data, build_data=True)
    return is_spam
