"""
django admin pages for certificates models
"""
from config_models.admin import ConfigurationModelAdmin
from django import forms
from django.contrib import admin

from certificates.models import (
    CertificateGenerationConfiguration,
    CertificateGenerationCourseSetting,
    CertificateHtmlViewConfiguration,
    CertificateTemplate,
    CertificateTemplateAsset,
    GeneratedCertificate
)
from util.organizations_helpers import get_organizations

# Sebas Imports
import logging
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin, ExportActionModelAdmin
from django.contrib.auth.models import User


class CertificateTemplateForm(forms.ModelForm):
    """
    Django admin form for CertificateTemplate model
    """
    def __init__(self, *args, **kwargs):
        super(CertificateTemplateForm, self).__init__(*args, **kwargs)
        organizations = get_organizations()
        org_choices = [(org["id"], org["name"]) for org in organizations]
        org_choices.insert(0, ('', 'None'))
        self.fields['organization_id'] = forms.TypedChoiceField(
            choices=org_choices, required=False, coerce=int, empty_value=None
        )

    class Meta(object):
        model = CertificateTemplate
        fields = '__all__'


class CertificateTemplateAdmin(admin.ModelAdmin):
    """
    Django admin customizations for CertificateTemplate model
    """
    list_display = ('name', 'description', 'organization_id', 'course_key', 'mode', 'is_active')
    form = CertificateTemplateForm


class CertificateTemplateAssetAdmin(admin.ModelAdmin):
    """
    Django admin customizations for CertificateTemplateAsset model
    """
    list_display = ('description', 'asset_slug',)
    prepopulated_fields = {"asset_slug": ("description",)}


class GeneratedCertificateResource(resources.ModelResource):
    username = fields.Field(attribute='username', column_name='username')
    email = fields.Field(attribute='email', column_name='email')
    user = fields.Field(attribute='user', column_name='user ID')

    class Meta:
        model = GeneratedCertificate
        fields = ('course_id','verify_uuid','grade','status','mode','name','created_date','user','username','email')
        export_order = ('user','username','course_id','verify_uuid','grade','status','mode','name','email','created_date')


    def dehydrate_username(self,obj):
        uname = ''
        try:
            objeto_user = User.objects.get(username=obj.user)
            uname = objeto_user.username
        except Exception as e:
            logging.info(e)
        return uname

    def dehydrate_email(self,obj):
        ema = ''
        try:
            objeto_user = User.objects.get(username=obj.user)
            ema = objeto_user.email
        except Exception as e:
            logging.info(e)
        return ema




class GeneratedCertificateAdmin(ExportActionModelAdmin):
    """
    Django admin customizations for GeneratedCertificate model
    """
    resource_class = GeneratedCertificateResource
    raw_id_fields = ('user',)
    show_full_result_count = False
    search_fields = ('course_id', 'user__username')
    list_display = ('id', 'course_id', 'mode', 'user')


class CertificateGenerationCourseSettingAdmin(admin.ModelAdmin):
    """
    Django admin customizations for CertificateGenerationCourseSetting model
    """
    list_display = ('course_key',)
    readonly_fields = ('course_key',)
    search_fields = ('course_key',)
    show_full_result_count = False


admin.site.register(CertificateGenerationConfiguration)
admin.site.register(CertificateGenerationCourseSetting, CertificateGenerationCourseSettingAdmin)
admin.site.register(CertificateHtmlViewConfiguration, ConfigurationModelAdmin)
admin.site.register(CertificateTemplate, CertificateTemplateAdmin)
admin.site.register(CertificateTemplateAsset, CertificateTemplateAssetAdmin)
admin.site.register(GeneratedCertificate, GeneratedCertificateAdmin)
