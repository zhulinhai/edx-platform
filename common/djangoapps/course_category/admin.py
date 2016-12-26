from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from models import CourseCategory, CourseCategoryCourse


class CourseAdmin(admin.StackedInline):
    fields = ['course_id',]
    model = CourseCategoryCourse


class CourseCategoryAdmin(DjangoMpttAdmin):
    tree_auto_open = True
    prepopulated_fields = {'slug': ('name',)}
    fields = ['name', 'slug', 'description', 'parent']
    inlines = [CourseAdmin,]


admin.site.register(CourseCategory, CourseCategoryAdmin)
