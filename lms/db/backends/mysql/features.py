from django.db.backends.mysql.features import DatabaseFeatures
from django.utils.functional import cached_property


class CustomDatabaseFeatures(DatabaseFeatures):
    """
    This class overrides DatabaseFeatures for djngo mysql backend,
    in order to fix supports_transactions problem launched by
    import_export admin library. The problem is documented here:
    https://code.djangoproject.com/ticket/26541

    This problem has been fixed in django 1.11:
    https://github.com/django/django/commit/6e4e0f4ce48b80495e89abbee030cf49809a9c54

    This override will be deprecated when Open Edx Hawthorn Release
    will be launched.
    """

    @cached_property
    def supports_transactions(self):
        """
        All storage engines except MyISAM support transactions.
        """
        return self._mysql_storage_engine != 'MyISAM'
