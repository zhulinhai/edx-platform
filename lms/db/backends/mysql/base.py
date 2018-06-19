from django.db.backends.mysql import base
from .features import CustomDatabaseFeatures


class DatabaseWrapper(base.DatabaseWrapper):
    """
    This class overrides DatabaseWrapper for djngo mysql backend,
    in order to fix supports_transactions problem launched by
    import_export admin library. The problem is documented here:
    https://code.djangoproject.com/ticket/26541

    This problem has been fixed in django 1.11:
    https://github.com/django/django/commit/6e4e0f4ce48b80495e89abbee030cf49809a9c54

    This override will be deprecated when Open Edx Hawthorn Release
    will be launched.
    """

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.features = CustomDatabaseFeatures(self)
