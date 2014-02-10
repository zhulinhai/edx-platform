"""
This is a localdev test for the Microsite processing pipeline
"""
# We intentionally define lots of variables that aren't used, and
# want to import all variables from base settings files
# pylint: disable=W0401, W0614

from .devstack import *


USE_I18N = True
LANGUAGES = ( ('es_419', 'Spanish'), )
TIME_ZONE = 'America/Bogota'
LANGUAGE_CODE = 'es_419'

SUBDOMAIN_BRANDING['edge'] = 'edge'
SUBDOMAIN_BRANDING['preview.edge'] = 'edge'
VIRTUAL_UNIVERSITIES = ['edge']

## Microsites

MICROSITE_CONFIGURATION = {
    "site1": {
        "domain_prefix": "site1",
        "university": "site1",
        "platform_name": "Prime Site",
        "logo_image_url": "site1/images/logo.jpg",
        "favicon_path": "site1/images/favicon.ico",
        "email_from_address": "openedx@site1.org",
        "payment_support_email": "openedx@site1.org",
        "ENABLE_MKTG_SITE": False,
        "SITE_NAME": "site1.v3.dev3.local",
        "course_org_filter": "edX",
        "course_about_show_social_links": False,
        "css_overrides_file": "site1/css/identity.css",
        "show_partners": False,
        "show_homepage_promo_video": False,
        "course_index_overlay_text": "Site 1. el mejor site",
        "course_index_overlay_logo_file": "/static/site1/images/logo-small.png",
        "homepage_overlay_html": "<h1>Im using a site</h1>",
    },
    "site2": {
        "domain_prefix": "site2",
        "university": "site2",
        "platform_name": "Other Site",
        "logo_image_url": "site2/images/logo.jpg",
        "favicon_path": "site2/images/favicon.png",
        "email_from_address": "openedx@site2.org",
        "payment_support_email": "openedx@site2.org",
        "ENABLE_MKTG_SITE": False,
        "course_org_filter": "afs",
        "SITE_NAME": "site2.v3.dev3.local",
        "course_about_show_social_links": False,
        "css_overrides_file": "site2/css/identity.css",
        "show_partners": False,
        "show_homepage_promo_video": True,
        "homepage_promo_video_youtube_id": "wte-k9mOtxs",
        "course_index_overlay_text": "Site 2. el mejor site",
        "course_index_overlay_logo_file": "/static/site2/images/logo-small.png",
        "homepage_overlay_html": "<h1>Im using a site2</h1>",
    }
}

if len(MICROSITE_CONFIGURATION.keys()) > 0:
    enable_microsites(
        MICROSITE_CONFIGURATION,
        SUBDOMAIN_BRANDING,
        VIRTUAL_UNIVERSITIES
    )

# pretend we are behind some marketing site, we want to be able to assert that the Microsite config values override
# this global setting
FEATURES['ENABLE_MKTG_SITE'] = False
MKTG_URLS = {
    'ABOUT': '/about-us',
    'CONTACT': '/contact-us',
    'FAQ': '/student-faq',
    'COURSES': '/courses',
    'ROOT': 'http://www.edunext.co',
    'TOS': '/edx-terms-service',
    'HONOR': '/terms',
    'PRIVACY': '/edx-privacy-policy',
    'WHAT_IS_VERIFIED_CERT': '/verified-certificate',
}
MKTG_URL_LINK_MAP = {
    'ABOUT': 'about_edx',
    'CONTACT': 'contact',
    'FAQ': 'help_edx',
    'COURSES': 'courses',
    'ROOT': 'root',
    'TOS': 'tos',
    'HONOR': 'honor',
    'PRIVACY': 'privacy_edx',
    'WHAT_IS_VERIFIED_CERT': 'verified-certificate',
}


# Edunext Main-Theme
#


THEME_NAME = 'edunext'
FEATURES['USE_CUSTOM_THEME'] = True
# Calculate the location of the theme's files
theme_root = ENV_ROOT / "themes" / THEME_NAME
# Include the theme's templates in the template search paths
TEMPLATE_DIRS.insert(0,theme_root / 'templates')
MAKO_TEMPLATES['main'].insert(0,theme_root / 'templates')

# Namespace the theme's static files to 'themes/<theme_name>' to
# avoid collisions with default edX static files
STATICFILES_DIRS.insert(0,(u'themes/%s' % THEME_NAME, theme_root / 'static'))
FAVICON_PATH = 'themes/%s/images/favicon.ico' % THEME_NAME
