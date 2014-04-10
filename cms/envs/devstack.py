"""
Specific overrides to the base prod settings to make development easier.
"""

from .aws import * # pylint: disable=wildcard-import, unused-wildcard-import

DEBUG = True
TEMPLATE_DEBUG = DEBUG

USE_I18N = True
LANGUAGES = ( ('es_419', 'Spanish'), )
TIME_ZONE = 'America/Bogota'
LANGUAGE_CODE = 'es_419'

################################ LOGGERS ######################################

import logging

# Disable noisy loggers
for pkg_name in ['track.contexts', 'track.middleware', 'dd.dogapi']:
    logging.getLogger(pkg_name).setLevel(logging.CRITICAL)


################################ EMAIL ########################################

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

################################# LMS INTEGRATION #############################

LMS_BASE = "localhost:8000"
FEATURES['PREVIEW_LMS_BASE'] = "preview." + LMS_BASE


FEATURES['ENABLE_CREATOR_GROUP'] = True
# FEATURES['STUDIO_REQUEST_EMAIL'] = 'felipe.montoya@edunext.co'

################################# CELERY ######################################

# By default don't use a worker, execute tasks as if they were local functions
CELERY_ALWAYS_EAGER = True

################################ DEBUG TOOLBAR ################################
INSTALLED_APPS += ('debug_toolbar', 'debug_toolbar_mongo')
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

# To see stacktraces for MongoDB queries, set this to True.
# Stacktraces slow down page loads drastically (for pages with lots of queries).
DEBUG_TOOLBAR_MONGO_STACKTRACES = False


CELERY_RESULT_BACKEND = 'database'
CELERY_CACHE_BACKEND = 'memory'


CACHES = {
    # This is the cache used for most things. Askbot will not work without a
    # functioning cache -- it relies on caching to load its settings in places.
    # In staging/prod envs, the sessions also live here.
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'edx_loc_mem_cache',
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },

    # The general cache is what you get if you use our util.cache. It's used for
    # things like caching the course.xml file for different A/B test groups.
    # We set it to be a DummyCache to force reloading of course.xml in dev.
    # In staging environments, we would grab VERSION from data uploaded by the
    # push process.
    'general': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'KEY_PREFIX': 'general',
        'VERSION': 4,
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },

    'mongo_metadata_inheritance': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/mongo_metadata_inheritance',
        'TIMEOUT': 300,
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },
    'loc_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'edx_location_mem_cache',
    },

}

# Make the keyedcache startup warnings go away
CACHE_TIMEOUT = 0

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

###############################################################################
# Lastly, see if the developer has any local overrides.
try:
    from .private import *  # pylint: disable=F0401
except ImportError:
    pass
