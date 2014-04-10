# -*- coding: utf-8 -*-
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

PLATFORM_NAME = "eduNEXT"

FAVICON_PATH = "themes/edunext/images/favicon.ico"

FEATURES['ENABLE_INSTRUCTOR_EMAIL'] = True

# Enable flow for payments for course registration (DIFFERENT from verified student flow)
FEATURES['ENABLE_PAID_COURSE_REGISTRATION'] = True,
# Toggle the availability of the shopping cart page
FEATURES['ENABLE_SHOPPING_CART'] = True,
# Toggle storing detailed billing information
FEATURES['STORE_BILLING_INFO'] = False,
# Setting for PAID_COURSE_REGISTRATION, DOES NOT AFFECT VERIFIED STUDENTS
PAID_COURSE_REGISTRATION_CURRENCY = ['cop', '$']

## Microsites

MICROSITE_CONFIGURATION = {
    # "prime": {
    #     "domain_prefix": "prime",
    #     "university": "prime",
    #     "platform_name": "Prime en eduNEXT",
    #     "logo_image_url": "prime/images/logo.jpg",
    #     "favicon_path": "prime/images/favicon.ico",
    #     "email_from_address": "prime@edunext.co",
    #     "payment_support_email": "prime@edunext.co",
    #     "ENABLE_MKTG_SITE": False,
    #     "SITE_NAME": "prime.edunext.co",
    #     "course_org_filter": "Prime",
    #     "course_about_show_social_links": False,
    #     "css_overrides_file": "prime/css/identity.css",
    #     "show_partners": False,
    #     "show_homepage_promo_video": False,
    #     "course_index_overlay_text": "<h1>Universidad Sergio Arboleda</h1><h2>Prime Bussiness School</h2>",
    #     "course_index_overlay_logo_file": "/static/prime/images/logo-small.png",
    #     "homepage_overlay_html": "<h1>Universidad Sergio Arboleda</h1><h2>Prime Bussiness School</h2>",
    # },
    # "afs": {
    #     "domain_prefix": "afs",
    #     "university": "afs",
    #     "platform_name": "AFS en eduNEXT",
    #     "logo_image_url": "afs/images/logo.jpg",
    #     "favicon_path": "afs/images/favicon.png",
    #     "email_from_address": "afs@edunext.co",
    #     "payment_support_email": "afs@edunext.co",
    #     "ENABLE_MKTG_SITE": False,
    #     "course_org_filter": "AFS",
    #     "SITE_NAME": "afs.edunext.co",
    #     "course_about_show_social_links": False,
    #     "css_overrides_file": "afs/css/identity.css",
    #     "show_partners": False,
    #     "show_homepage_promo_video": True,
    #     "homepage_promo_video_youtube_id": "wte-k9mOtxs",
    #     "course_index_overlay_text": "<h1>Connecting Lives,</h1><h2>Sharing Cultures</h2>",
    #     "course_index_overlay_logo_file": "/static/afs/images/logo-small.png",
    #     "homepage_overlay_html": "<h1>Connecting Lives,</h1><h2>Sharing Cultures</h2>",
    # },
    # "labranzacero": {
    #     "domain_prefix": "test2",
    #     "university": "labranzacero",
    #     "platform_name": "Labranza Cero en eduNEXT",
    #     "logo_image_url": "labranzacero/images/logo_labranza_cero.png",
    #     "favicon_path": "labranzacero/images/favicon.ico",
    #     "email_from_address": "labranzacero@edunext.co",
    #     "payment_support_email": "labranzacero@edunext.co",
    #     "ENABLE_MKTG_SITE": False,
    #     "course_org_filter": "Labranzacero",
    #     "SITE_NAME": "labranzacero.edunext.co",
    #     "course_about_show_social_links": False,
    #     "css_overrides_file": "labranzacero/css/identity.css",
    #     "show_partners": False,
    #     "show_homepage_promo_video": False,
    #     "homepage_overlay_html": "<img src='/static/labranzacero/images/labranza_cero_head.png'><h1>Su marca en el corazón</h1>",
    #     "course_index_overlay_text": "<h1>Cursos actuales de Labranza Cero</h1>",
    #     "course_index_overlay_logo_file": "/static/labranzacero/images/logo-small.png",
    # },
    "paqua": {
        "domain_prefix": "test",
        "university": "paqua",
        "platform_name": "Paqua en eduNEXT",
        "logo_image_url": "paqua/images/logo.jpg",
        "favicon_path": "paqua/images/favicon.ico",
        "email_from_address": "paqua@edunext.co",
        "payment_support_email": "paqua@edunext.co",
        "ENABLE_MKTG_SITE": False,
        "course_org_filter": "Paqua",
        "SITE_NAME": "paqua.edunext.co",
        "course_about_show_social_links": False,
        "css_overrides_file": "paqua/css/identity.css",
        "show_partners": False,
        "show_homepage_promo_video": False,
        "homepage_overlay_html": "<img src='/static/paqua/images/paqua-large.png'>",
        "course_index_overlay_text": "<h1>Cultivando Comunidad</h1>",
        "course_index_overlay_logo_file": "/static/paqua/images/logo-small.jpg",
    },
    "sca": {
        "domain_prefix": "test2",
        "university": "sca",
        "platform_name": "Sociedad Colombiana de Archivistas",
        "logo_image_url": "sca/images/logo.jpg",
        "favicon_path": "sca/images/favicon.ico",
        "email_from_address": "scarchivistas@edunext.co",
        "payment_support_email": "scarchivistas@edunext.co",
        "ENABLE_MKTG_SITE": False,
        "course_org_filter": "afs",
        "SITE_NAME": "scarchivistas.edunext.co",
        "course_about_show_social_links": False,
        "css_overrides_file": "sca/css/identity.css",
        "show_partners": False,
        "show_homepage_promo_video": False,
        "homepage_overlay_html": "<h1>Sociedad Colombiana de Archivistas</h1><h2>Plataforma de capacitación</h2>",
        "course_index_overlay_text": "<h1>Plan de capacitaciones para 2014</h1>",
        "course_index_overlay_logo_file": "/static/sca/images/logo-small.png",
    },
    # "innova-tic": {
    #     "domain_prefix": "innova-tic",
    #     "university": "innova-tic",
    #     "platform_name": "Innova-tic en eduNEXT",
    #     "logo_image_url": "innova-tic/images/logo.jpg",
    #     "favicon_path": "innova-tic/images/favicon.png",
    #     "email_from_address": "innova-tic@edunext.co",
    #     "payment_support_email": "innova-tic@edunext.co",
    #     "ENABLE_MKTG_SITE": False,
    #     "course_org_filter": "Innova-tic",
    #     "SITE_NAME": "innova-tic.com",
    #     "course_about_show_social_links": False,
    #     "css_overrides_file": "innova-tic/css/identity.css",
    #     "show_partners": False,
    #     "show_homepage_promo_video": False,
    #     "course_index_overlay_text": "<h1>Cursos actuales de innova-tic</h2>",
    #     "course_index_overlay_logo_file": "/static/innova-tic/images/logo-small.png",
    #     "homepage_overlay_html": "<h1>Borrame,</h1><h2>pronto</h2>",
    # },
    # "pleisi": {
    #     "domain_prefix": "pleisi",
    #     "university": "pleisi",
    #     "platform_name": "Academia Pleisi",
    #     "course_org_filter": "Pleisi",
    #     "SITE_NAME": "academia.pleisi.com",
    #     "logo_image_url": "pleisi/images/logo.jpg",
    #     "favicon_path": "pleisi/images/favicon.png",
    #     "css_overrides_file": "pleisi/css/identity.css",
    #     "email_from_address": "pleisi@edunext.co",
    #     "payment_support_email": "pleisi@edunext.co",
    #     "show_homepage_promo_video": False,
    #     "homepage_overlay_html": "<h1>Borrame,</h1><h2>pronto</h2>",
    #     "course_index_overlay_text": "<h1>Cursos de la academia pleisi</h2>",
    #     "course_index_overlay_logo_file": "/static/pleisi/images/logo-small.png",
    #     "ENABLE_MKTG_SITE": False,
    #     "show_partners": False,
    #     "course_about_show_social_links": False,
    # },
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
    'COURSES': 'courses',
    'ROOT': 'root',
    'TOS': 'tos',
    'HONOR': 'honor',
    'PRIVACY': 'privacy_edx',
    'WHAT_IS_VERIFIED_CERT': 'verified-certificate',
}


# Edunext Main-Theme
#
from .theme import enable_theme
THEME_NAME = "edunext"
enable_theme(THEME_NAME)

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
