from cms.envs.devstack import *


CMS_BASE = 'localhost:8001'
FEATURES.update({
    'USE_DJANGO_PIPELINE': False,
})
