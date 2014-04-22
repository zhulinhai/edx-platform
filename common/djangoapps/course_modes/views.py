"""
Views for the course_mode module
"""

import decimal
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponseBadRequest,  Http404
)
from django.shortcuts import redirect
from django.views.generic.base import View
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime

from edxmako.shortcuts import render_to_response, render_to_string

from course_modes.models import CourseMode
from courseware.access import has_access
from student.models import CourseEnrollment
from student.views import course_from_id
from verify_student.models import SoftwareSecurePhotoVerification

from microsite_configuration.middleware import MicrositeConfiguration
from django.core.mail import send_mail
from smtplib import SMTPException
from shoppingcart.views import add_course_to_cart
from shoppingcart.models import Order, PaidCourseRegistration

class ChooseModeView(View):
    """
    View used when the user is asked to pick a mode

    When a get request is used, shows the selection page.
    When a post request is used, assumes that it is a form submission
        from the selection page, parses the response, and then sends user
        to the next step in the flow
    """
    @method_decorator(login_required)
    def get(self, request, course_id, error=None):
        """ Displays the course mode choice page """

        enrollment_mode = CourseEnrollment.enrollment_mode_for_user(request.user, course_id)
        upgrade = request.GET.get('upgrade', False)
        request.session['attempting_upgrade'] = upgrade

        # verified users do not need to register or upgrade
        if enrollment_mode == 'verified':
            return redirect(reverse('dashboard'))

        # registered users who are not trying to upgrade do not need to re-register
        if enrollment_mode is not None and upgrade is False:
            return redirect(reverse('dashboard'))

        modes = CourseMode.modes_for_course_dict(course_id)
        donation_for_course = request.session.get("donation_for_course", {})
        chosen_price = donation_for_course.get(course_id, None)

        course = course_from_id(course_id)
        context = {
            "course_id": course_id,
            "modes": modes,
            "course_name": course.display_name_with_default,
            "course_org": course.display_org_with_default,
            "course_num": course.display_number_with_default,
            "chosen_price": chosen_price,
            "error": error,
            "upgrade": upgrade,
        }
        if "paid" in modes:
            context["suggested_prices"] = [decimal.Decimal(x) for x in modes["paid"].suggested_prices.split(",")]
            context["currency"] = modes["paid"].currency.upper()
            context["min_price"] = modes["paid"].min_price

            cart = Order.get_cart_for_user(request.user)
            context["in_cart"] = PaidCourseRegistration.contained_in_order(cart, course_id)


        return render_to_response("course_modes/choose.html", context)

    @method_decorator(login_required)
    def post(self, request, course_id):
        """ Takes the form submission from the page and parses it """
        user = request.user

        # This is a bit redundant with logic in student.views.change_enrollement,
        # but I don't really have the time to refactor it more nicely and test.
        course = course_from_id(course_id)
        if not has_access(user, course, 'enroll'):
            error_msg = _("Enrollment is closed")
            return self.get(request, course_id, error=error_msg)

        upgrade = request.GET.get('upgrade', False)

        requested_mode = self.get_requested_mode(request.POST)

        allowed_modes = CourseMode.modes_for_course_dict(course_id)
        if requested_mode not in allowed_modes:
            return HttpResponseBadRequest(_("Enrollment mode not supported"))

        if requested_mode in ("audit", "honor", "free"):
            CourseEnrollment.enroll(user, course_id, requested_mode)
            return redirect('dashboard')

        if requested_mode == "manual":
            return redirect('course_modes_manual', course_id=course_id)

        mode_info = allowed_modes[requested_mode]

        if requested_mode == "paid":
            response = add_course_to_cart(request,course_id)
            # happy path
            if response.status_code < 400:
                return redirect(reverse('shoppingcart.views.show_cart'))
            # sad path
            else:
                return response

        if requested_mode == "verified":
            amount = request.POST.get("contribution") or \
                request.POST.get("contribution-other-amt") or 0

            try:
                # validate the amount passed in and force it into two digits
                amount_value = decimal.Decimal(amount).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
            except decimal.InvalidOperation:
                error_msg = _("Invalid amount selected.")
                return self.get(request, course_id, error=error_msg)

            # Check for minimum pricing
            if amount_value < mode_info.min_price:
                error_msg = _("No selected price or selected price is too low.")
                return self.get(request, course_id, error=error_msg)

            donation_for_course = request.session.get("donation_for_course", {})
            donation_for_course[course_id] = amount_value
            request.session["donation_for_course"] = donation_for_course
            if SoftwareSecurePhotoVerification.user_has_valid_or_pending(request.user):
                return redirect(
                    reverse('verify_student_verified',
                            kwargs={'course_id': course_id}) + "?upgrade={}".format(upgrade)
                )

            return redirect(
                reverse('verify_student_show_requirements',
                        kwargs={'course_id': course_id}) + "?upgrade={}".format(upgrade))

    def get_requested_mode(self, request_dict):
        """
        Given the request object of `user_choice`, return the
        corresponding course mode slug
        """
        # if 'audit_mode' in request_dict:
        #     return 'audit'
        # if 'certificate_mode' and request_dict.get("honor-code"):
        #     return 'honor'
        # if 'certificate_mode' in request_dict:
        #     return 'verified'
        if 'manual_mode' in request_dict:
            return 'manual'
        if 'free_mode' in request_dict:
            return 'free'
        if 'paid_mode' in request_dict:
            return 'paid'

class ChosedManualView(View):
    """
    View used when the user chooses the manual mode

    When a get request is used, shows the contact form.
    When a post request is used, assumes that it is a form submission
        from the contact page
    """
    @method_decorator(login_required)
    def get(self, request, course_id, error=None):
        """ Displays a contact form page """

        enrollment_mode = CourseEnrollment.enrollment_mode_for_user(request.user, course_id)

        # registered users do not need to re-register
        if enrollment_mode is not None:
            return redirect(reverse('dashboard'))

        self.notify_course_support(request, course_id)

        modes = CourseMode.modes_for_course_dict(course_id)
        course = course_from_id(course_id)
        context = {
            "course_id": course_id,
            "modes": modes,
            "course_name": course.display_name_with_default,
            "course_org": course.display_org_with_default,
            "course_num": course.display_number_with_default,
            "error": error,
        }
        return render_to_response("course_modes/manual.html", context)

    def notify_course_support(self, request, course_id):
        """ Emails the course staff from the site/microsite """
        to_address = MicrositeConfiguration.get_microsite_configuration_value(
            'registration_email',
            'cursos@edunext.co'
        )
        site_name = MicrositeConfiguration.get_microsite_configuration_value(
            'platform_name',
            'edunext'
        )
        user = request.user
        time = datetime.now()
        context = {
            'user_name': user.username,
            'user_realname': user.profile.name,
            'user_email': user.email,
            'course_id': course_id,
            'site_name':site_name,
            'to_address':to_address,
            'time':time,
        }

        subject = render_to_string('emails/manual_registration_course_subject.txt', context)
        subject = ''.join(subject.splitlines())
        message = render_to_string('emails/manual_registration_course.txt', context)

        try:
            send_mail(
                subject,
                message,
                'no-reply@edunext.co',
                [to_address],
                fail_silently=False
            )
        except SMTPException:
            log.warning("Failure sending 'manual registration' e-mail for %s to %s", user.email, to_address)

