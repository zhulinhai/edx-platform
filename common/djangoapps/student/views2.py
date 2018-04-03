# -*- coding: utf-8 -*-
import datetime
from student.models import CourseEnrollment
from student.views import _update_email_opt_in
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from opaque_keys.edx.keys import CourseKey
from django.views.decorators.clickjacking import xframe_options_exempt
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from course_modes.models import CourseMode
from student.models import (
    Registration, UserProfile,
    PendingEmailChange, CourseEnrollment, CourseEnrollmentAttribute, unique_id_for_user,
    CourseEnrollmentAllowed, UserStanding, LoginFailures,
    create_comments_service_user, PasswordHistory, UserSignupSource,
    DashboardConfiguration, LinkedInAddToProfileConfiguration, ManualEnrollmentAudit, ALLOWEDTOENROLL_TO_ENROLLED,
    LogoutViewConfiguration)
from xmodule.modulestore.django import modulestore
from django.shortcuts import redirect
import logging
from django.conf import settings
from django.utils.translation import ugettext as _
from openedx.core.djangoapps.embargo import api as embargo_api
from ipware.ip import get_ip
from django.core.urlresolvers import reverse
from util.db import outer_atomic
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from opaque_keys import InvalidKeyError
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
# from smtplib import SMTP_SSL as SMTP
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
from django.conf import settings
from email.utils import formataddr
from email.header import Header
from views import send_mailX

log = logging.getLogger("edx.student")
plantilla_email = "<table border=0 cellpadding=0 cellspacing=0 style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;width:650px align=center width=650><tr><td height=10 valign=middle align=left> <tr><td valign=top style=background-color:#dbf2ff><table border=0 cellpadding=0 cellspacing=0 style=width:648px><tr><td height=10 width=3%> <td height=10 width=94%> <td height=10 width=3%> <tr><td width=3%> <td width=94% style=font-family:Arial,Helvetica,sans-serif;font-size:24px;color:#db5008><strong>Formulario Contáctanos</strong><td width=3%> <tr><td height=10> <td height=10 valign=top> <td height=10> <tr><td> <td valign=top><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px>Estimado administrador <strong></strong>:<br><br>Se registró el siguiente formulario para su revisión:<br><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px>Nombre completo:<strong>{nombreCompleto}</strong><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px>Email:<strong>{email}</strong><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px>Región:<strong>{region}</strong><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px>Curso:<strong>{curso}</strong><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px>Teléfono:<strong>{telefono}</strong><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px>Tema:<strong>{tema}</strong><p style=font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#585858;line-height:16px><strong></strong>Descripción:<br><strong>{descripcion}</strong><p><br><td> <tr><td height=10> <td height=10> <td height=10> </table><tr><td style=background-color:#0087ce><table border=0 cellpadding=0 cellspacing=0 style=width:648px><tr><td height=10> <td height=10> <td height=10> <td height=10> <tr><td width=3%> <td width=47% align=left valign=top><p style=font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#fff;line-height:14px><td width=47% align=right valign=top><p style=font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#fff;line-height:14px><strong>Campus Romero</strong><br><a href=https://www.campusromero.pe target=_blank style=font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#fff;line-height:14px;text-decoration:none>www.campusromero.pe</a><td width=3%> <tr><td height=10> <td height=10> <td height=10> <td height=10> </table>"

# ITSoluciones
@xframe_options_exempt
def iframe_log_reg(request):
    user = request.user
    context = {'user': user}
    return render_to_response('iframe_login.html', context)


# ITSoluciones
@xframe_options_exempt
def purchase_course(request, course_id):
    user = request.user
    p_course = course_id
    bool_ac = False
    bool_in = False
    syserror = ''

    # 1.Datos basicos del curso si existe
    try:
        course_id = SlashSeparatedCourseKey.from_deprecated_string(p_course)
        course = modulestore().get_course(course_id)
        student_enrolled = CourseEnrollment.is_enrolled(request.user, course_id)
        analytics = p_course.split("+")[1]

        import pytz
        lima = pytz.timezone("America/Lima")
        date_time = lima.localize(datetime.datetime.now())

        if course.start.date() == date_time.date():
            if course.start.time() >= date_time.time():
                bool_ac = True
        elif course.start.date() > date_time.date():
            bool_ac = True

        if not course.enrollment_start or not course.enrollment_end:
            if not course.enrollment_end:
                if date_time.date() == course.end.date():
                    if date_time.time() <= course.end.time():
                        bool_in = True
                elif date_time.date() < course.end.date():
                    bool_in = True
            elif not course.enrollment_start:
                if date_time.date() == course.enrollment_end.date():
                    if date_time.time() <= course.enrollment_end.time():
                        bool_in = True
                elif date_time.date() < course.enrollment_end.date():
                    bool_in = True

        else:
            if course.enrollment_start.date() == date_time.date():
                if course.enrollment_start.time() <= date_time.time():
                    if course.enrollment_end.date() > date_time.date():
                        bool_in = True
                    if course.enrollment_end.date() == date_time.date():
                        if course.enrollment_end.time() > date_time.time():
                            bool_in = True
            elif course.enrollment_start.date() < date_time.date():
                if course.enrollment_end.date() > date_time.date():
                    bool_in = True
                if course.enrollment_end.date() == date_time.date():
                    if course.enrollment_end.time() > date_time.time():
                        bool_in = True
    except Exception as e:
        context = {
            'error': "CURSO NO EXISTENTE",
            'exception': e,
            'user': user,
            'cod_course': p_course
        }
        return render_to_response('purchase_course.html', context)

    # 2.Verificar si el curso esta abierto
    if not bool_in and not student_enrolled:
        context = {
            'error': "INSCRIPCION CERRADA",
            'user': user,
            'cod_course': p_course
        }
        return render_to_response('purchase_course.html', context)
    sku = ""
    # 3.Obtener datos si es examen

    # Magia Digital - VD, integracion con el e-commerce
    # modalidad de curso no-id-professional va directamente al ecommerce
    # modalidad audit o verified lleva a la pantalla de eleccion

    courseMode = None

    try:

        CourseDict = CourseMode.modes_for_course_dict(course_id)

        for key in CourseDict.keys():
            if key == 'no-id-professional':
                sku = CourseMode.modes_for_course_dict(course_id)[key].sku
                price = CourseMode.modes_for_course_dict(course_id)[key].min_price
                exp_date = CourseMode.modes_for_course_dict(course_id)[key].expiration_datetime
                is_payment = CourseMode.objects.filter(course_id=course_id).exists()

                if exp_date:
                    exp_date = exp_date.strftime("%d/%m/%Y")
            else:
                price = None
                exp_date = None
                is_payment = None
    except KeyError as e:
        price = None
        exp_date = None
        is_payment = None
        syserror = CourseMode.modes_for_course_dict(course_id)
    # 4.Obtener datos del usuario
    user = request.user
    if not user.is_authenticated():
        user_p = ''
    else:
        user_p = UserProfile.objects.get(user=request.user)

    # 5.Logica de inscripcion
    # cursos_gr = None
    is_course_payment = is_payment and price > 0
    context = {'cod_course': p_course, "analytics": analytics, 'student_enrolled': student_enrolled, "ins": bool_in,
               'user': user, 'price': price, 'user_p': user_p, "still_start": bool_ac,
               "exp_date": exp_date, "is_payment": is_payment, "is_course_payment": is_course_payment, "sku": sku, "syserror": syserror}

    return render_to_response('purchase_course.html', context)


@transaction.non_atomic_requests
@require_POST
@outer_atomic(read_committed=True)
def change_enrollment(request, course_id, check_access=True):

    if(request.method == 'POST'):
        try:
            CourseEnrollment.enroll(request.user, CourseKey.from_string(course_id))
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(str(e), status=500)
    else:
        return HttpResponse(status=404)


def noLoginBasket(request, sku):
    return redirect("https://pago.campusromero.pe/basket/single-item/?sku=" + sku)


def noLogingVerified(request, course_id):
    try:
        CourseEnrollment.enroll(request.user, CourseKey.from_string(course_id))
        return HttpResponseRedirect("https://cursos.campusromero.pe/course_modes/choose/" + course_id + "/")
    except Exception as e:
        return HttpResponse(str(e), status=500)


def enviarMail(mail, body, name):

    # Configuracion de inicio
    '''
    SMTPserver = 'mail.magiadigital.com'
    USERNAME = 'envios'
    PASSWORD = 'env10s'

    '''

    SMTPserver = settings.EMAIL_HOST
    USERNAME = settings.EMAIL_HOST_USER
    PASSWORD = settings.EMAIL_HOST_PASSWORD
    WEBMASTER = settings.CONTACT_EMAIL

    # Variables de inicio

    sender = WEBMASTER
    receiver = WEBMASTER  # 'dramos@magiadigital.com'
    msg = MIMEMultipart()

    msg['From'] = name + '<' + mail + '>'
    msg['to'] = receiver

    html = MIMEText(body, 'html', _charset='utf-8')
    msg.attach(html)
    msg['Subject'] = ("Formulario de contáctanos")

    # Envio del mensaje
    conn = smtplib.SMTP(SMTPserver)
    conn.set_debuglevel(False)
    conn.login(USERNAME, PASSWORD)

    try:
        conn.sendmail(sender, receiver, msg.as_string())
        log.info("---------------------->ENVIADO<------------------------")

        return True
    except Exception as e:
        log.info(e)
        return False
    finally:
        conn.quit()


class contactanos(APIView):
    '''
    {
       "usuario":{
          "nombreCompleto":"APPROVED",
          "email":"dramos@magiadigital.com",
          "region":"Perú",
          "curso":"Rocket fuel",
          "telefono":"978725447",
          "tema":"Composición química",
          "descripcion":"¿Cómo puedo hacer para que la combustión propagada por la explosión 
                         no pueda ser apagada facilmente"
       }
    }

    '''
    def post(self, request):

        log.info("---------------------->CONFIRMADO<------------------------")
        data = request.data.get('usuario', {})
        nombreCompleto = data.get('nombreCompleto', '')
        email = data.get('email', '')
        region = data.get('region', '')
        curso = data.get('curso', '')
        telefono = data.get('telefono', '')
        tema = data.get('tema', '')
        descripcion = data.get('descripcion', '')

        body = plantilla_email.replace('{nombreCompleto}', nombreCompleto.encode('utf-8')).replace('{email}', email.encode('utf-8')).replace('{region}', region.encode('utf-8')).replace('{curso}', curso.encode('utf-8')).replace('{telefono}', telefono.encode('utf-8')).replace('{tema}', tema.encode('utf-8')).replace('{descripcion}', descripcion.encode('utf-8'))
        logging.info('email: -----------')
        logging.info(email)
        logging.info('str(body): -----------')
        logging.info(str(body))
        logging.info('nombreCompleto: ----------')
        logging.info(nombreCompleto)
        logging.info('PRUEBAS OK ----------')


        # unicode(str(body),"utf-8")

        enviarMail(email, str(body), nombreCompleto)
        logging.info('ENVIADO OK ----------')

        return Response(
            status=status.HTTP_200_OK,
            data={
                "message": "Confirmado",
                "data": data
            },
            headers={'Access-Control-Allow-Origin': '*'},
        )

