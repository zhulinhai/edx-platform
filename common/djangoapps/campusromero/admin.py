from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

# Sebas Imports
import logging
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from student.models import UserProfile
from django.contrib.auth.hashers import make_password
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.contrib.admin import SimpleListFilter
from datetime import date

from django.contrib.auth.admin import UserAdmin

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

admin.site.unregister(User, UserAdmin)

class UserResource(resources.ModelResource):
    #columnas de UserProfile
    
    mailing_address = fields.Field(attribute='mailing_address',column_name='dni')
    location = fields.Field(attribute='location',column_name='telefono')

    name = fields.Field(attribute='name')
    gender = fields.Field(attribute='gender')
    city = fields.Field(attribute='city')
    day_of_birth = fields.Field(attribute='day_of_birth')    
    month_of_birth = fields.Field(attribute='month_of_birth')
    year_of_birth = fields.Field(attribute='year_of_birth')
    goals = fields.Field(attribute='goals', column_name='institucion')
    password = fields.Field(attribute='password')
    # falta COUNTRY y LANGUAGE
    level_of_education = fields.Field(attribute='level_of_education')    


    class Meta:
        model = User
        
        import_id_fields=['id']

    
        fields = ('username','first_name','last_name','email','mailing_address','location','id',
            'name','gender','city','year_of_birth','goals','password','date_joined','date_joined',
            'day_of_birth','month_of_birth','level_of_education')
        export_order = ('id','username','first_name','last_name','password','email','mailing_address','location',
            'name','gender','city','day_of_birth','month_of_birth','year_of_birth','goals','date_joined','level_of_education')
        # exclude = ('password')

    
    def dehydrate_mailing_address(self,obj):
        try:
            # import
            mailing_address = obj.mailing_address
            if mailing_address == '':
                mailing_address = UserProfile.objects.get(user=obj).mailing_address
        except:
            # export
            try: 
                mailing_address = UserProfile.objects.get(user=obj).mailing_address
            except:
                mailing_address = ''
        return mailing_address

    def dehydrate_location(self,obj):
        try:
            # import
            location = obj.location
            if location == '':
                location = UserProfile.objects.get(user=obj).location
        except:
            # export
            try:
                location = UserProfile.objects.get(user=obj).location
            except:
                location = ''
        return location

    def dehydrate_name(self,obj):
        try:
            # import
            name = obj.name
            if name == '':
                name = UserProfile.objects.get(user=obj).name
        except:
            # export
            try:
                name = UserProfile.objects.get(user=obj).name
            except:
                name = ''
        return name

    def dehydrate_gender(self,obj):
        try:
            # import
            gender = obj.gender
            if gender == '':
                gender = UserProfile.objects.get(user=obj).gender
        except:
            # export
            try: 
                gender = UserProfile.objects.get(user=obj).gender
            except:
                gender = ''
        return gender

    def dehydrate_city(self,obj):
        try:
            # import
            city = obj.city
            if city == '':
                city = UserProfile.objects.get(user=obj).city
        except:
            # export
            try: 
                city = UserProfile.objects.get(user=obj).city
            except:
                city = ''
        return city

    def dehydrate_day_of_birth(self,obj):
        try:
            # import
            day_of_birth = obj.day_of_birth
            if day_of_birth == '':
                day_of_birth = UserProfile.objects.get(user=obj).day_of_birth
        except:
            # export
            try:
                day_of_birth = UserProfile.objects.get(user=obj).day_of_birth
            except:
                day_of_birth = ''
        return day_of_birth    

    def dehydrate_month_of_birth(self,obj):
        try:
            # import
            month_of_birth = obj.month_of_birth
            if month_of_birth == '':
                month_of_birth = UserProfile.objects.get(user=obj).month_of_birth
        except:
            # export
            try:
                month_of_birth = UserProfile.objects.get(user=obj).month_of_birth
            except:
                month_of_birth = ''
        return month_of_birth    

    def dehydrate_year_of_birth(self,obj):
        try:
            # import
            year_of_birth = obj.year_of_birth
            if year_of_birth == '':
                year_of_birth = UserProfile.objects.get(user=obj).year_of_birth
        except:
            # export
            try:
                year_of_birth = UserProfile.objects.get(user=obj).year_of_birth
            except:
                year_of_birth = ''
        return year_of_birth

    def dehydrate_goals(self,obj):
        try:
            # import
            goals = obj.goals
            if goals == '':
                goals = UserProfile.objects.get(user=obj).goals
        except:
            # export
            try: 
                goals = UserProfile.objects.get(user=obj).goals
            except:
                goals = ''
        return goals

    def dehydrate_level_of_education(self,obj):
        try:
            # import
            level_of_education = obj.level_of_education
            if level_of_education == '':
                level_of_education = UserProfile.objects.get(user=obj).level_of_educationals
        except:
            # export
            try: 
                level_of_education = UserProfile.objects.get(user=obj).level_of_education
            except:
                level_of_education = ''
        return level_of_education

    def before_save_instance(self, instance, using_transactions, dry_run):

        # Validacion mail -------
        mail_repetido = False
        el_error = 'Advertencia_Sbs1: \"Duplicate entry \'' + str(instance.email) + '\' for key \'email\''

        # nuevo registro
        if instance.id == None:
            try:
                # existe un objeto con el mismo mail?
                objeto_prueba = User.objects.get(email=instance.email)
                mail_repetido = True            
            except:
                pass
        # actualizar registro
        else:
            if instance.email != '':

                # es igual al mail actual del objeto?
                objeto_prueba = User.objects.get(id=instance.id)
                if instance.email == objeto_prueba.email:
                    logging.info('si es igual, esto esta permitido. Termina la validacion')
                else:
                    # es igual al mail de algun otro objeto?
                    try:
                        objeto_prueba2 = User.objects.get(email=instance.email)
                        mail_repetido = True
                    except:
                        pass

        if mail_repetido == True:
            raise Exception(el_error)





        # ----- Procesamos el password -----

        # Si usuario no existe
        if instance.id == None or instance.id == '':
            
            new_pass = ''
            # password en blanco
            if instance.password == '':
                new_pass = '1234'
            # password numero
            elif str(instance.password)[-2:] == '.0':
                new_pass = str(instance.password)[:-2]
            # password string
            else:
                new_pass = str(instance.password)
            instance.password = make_password(new_pass,salt=None,hasher='default')




        # Si usuario existe
        else:            

            if str(instance.password)[:+13] == 'pbkdf2_sha256':
                logging.info('no hacer nada, es pass encriptada')
            elif str(instance.password)[-2:] == '.0':
                instance.password = str(instance.password)[:-2]
                instance.password = make_password(instance.password,salt=None,hasher='default')
            elif str(instance.password) != '':
                instance.password = make_password(str(instance.password),salt=None,hasher='default')


            try:
                existente = User.objects.get(id=instance.id)

                if instance.username == '' :
                    instance.username = existente.username

                if instance.email == '':
                    instance.email = existente.email

                if instance.first_name == '':
                    instance.first_name = existente.first_name

                if instance.last_name == '':
                    instance.last_name = existente.last_name

                if instance.password == '':
                    instance.password = existente.password

                instance.date_joined = existente.date_joined               

                '''
                if instance.date_joined == '':
                    instance.date_joined = existente.date_joined
                '''


            except Exception as e:
                logging.info(e)

    def after_save_instance(self, instance, using_transactions, dry_run):
        if not dry_run:

            # modificamos mailing_address y location para que no sean float
            if str(instance.mailing_address)[-2:] == '.0':
                instance.mailing_address = str(instance.mailing_address)[:-2]

            if str(instance.location)[-2:] == '.0':
                instance.location = str(instance.location)[:-2]  



            #intento de actualizar
            try:
                existente = UserProfile.objects.get(user=instance)
                if existente != None:
                    with transaction.atomic():

                        if instance.mailing_address != '':
                            existente.mailing_address = instance.mailing_address

                        if instance.location != '':
                            existente.location = instance.location

                        if instance.name != '':
                            existente.name = instance.name

                        if instance.gender != '':
                            existente.gender = instance.gender

                        if instance.city != '':
                            existente.city = instance.city

                        if instance.day_of_birth != '':
                            existente.day_of_birth = instance.day_of_birth

                        if instance.month_of_birth != '':
                            existente.month_of_birth = instance.month_of_birth                            

                        if instance.year_of_birth != '':
                            existente.year_of_birth = instance.year_of_birth

                        if instance.goals != '':
                            existente.goals = instance.goals


                        logging.info('probamos actualizar')
                        existente.save()
                        logging.info('prueba:')
                        logging.info(UserProfile.objects.get(user=instance).goals)
                        logging.info('funcionooooooooo')
            except Exception as e:
                logging.info(e)




            #intento de guardar por primera vez                     
            try:
                with transaction.atomic():
                    nuevo_UserProfile  = UserProfile(user=instance, mailing_address=instance.mailing_address, location=instance.location,
                        name=instance.name,gender=instance.gender,city=instance.city,goals=instance.goals)
                    
                    if instance.day_of_birth != '' or None:
                        nuevo_UserProfile.day_of_birth = instance.day_of_birth  

                    if instance.month_of_birth   != '' or None:
                        nuevo_UserProfile.month_of_birth = instance.month_of_birth  

                    if instance.year_of_birth != '' or None:
                        nuevo_UserProfile.year_of_birth = instance.year_of_birth    

                    logging.info('empezamos a guardar:')
                    nuevo_UserProfile.save()
                    logging.info('guardado con ...... Eeeeeeeexitoo')

                    # intentamos guardar password

            except Exception as a:
                logging.info('se cayo :(')
                logging.info(a)


        else:
            logging.info('after')
 

class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff'
        ,'date_joined','Fecha_de_nacimiento')
    list_filter = ('is_staff', 'is_superuser', 'is_active',
        ('date_joined', DateRangeFilter),('nacimiento',DateRangeFilter),)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    # Cambio de Sebas
    def Fecha_de_nacimiento(self, obj):
        try:
            var = date(obj.nacimiento.year,obj.nacimiento.month,obj.nacimiento.day)
        except:
            var = ""
        return var

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(UserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(UserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        return [
            url(r'^(.+)/password/$', self.admin_site.admin_view(self.user_change_password), name='auth_user_password_change'),
        ] + super(UserAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(UserAdmin, self).lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(UserAdmin, self).add_view(request, form_url,
                                               extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(id))
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(self.model._meta.verbose_name),
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(admin.site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST['_continue'] = 1
        return super(UserAdmin, self).response_add(request, obj,
                                                   post_url_continue)


#admin.site.register(User, UserAdmin)