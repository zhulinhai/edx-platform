from lms.envs.devstack import *


FEATURES.update({
    'ENABLE_COURSEWARE_SEARCH': False,
    'USE_DJANGO_PIPELINE': False,
})
# Begin test code
ADMINS=[('Name', 'test@example.com')]
# End test code
