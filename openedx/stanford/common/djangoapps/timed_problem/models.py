import datetime

from django.utils.timezone import UTC

from xblock.fields import Integer
from xblock.fields import Scope

from xmodule.fields import Date

_ = lambda text: text


class WarningFieldSingleValueMixin(object):
    """
    Wraps around the actual value of another xmodule.field.Field.
    If the value of this field is set on the front-end, a warning
    from the backend is shown
    """
    def __init__(self, warning=None, warning_condition=None, **kwargs):
        super(WarningFieldSingleValueMixin, self).__init__(**kwargs)
        self._values = {
            'warning': warning,
        }


class IntegerWithWarningField(WarningFieldSingleValueMixin, Integer):
    """
    Integer with a warning field built-in. The warning is triggered
    when the field name is specified under a certain condition
    """
    def __init__(self, **kwargs):
        super(IntegerWithWarningField, self).__init__(**kwargs)


class TimedCapaFields(object):
    minutes_before_warning = Integer(
        help=_(
            'Number of minutes at which the student will be issued a time warning. '
            'Works only when minutes_allowed is non-zero'
        ),
        default=1,
        scope=Scope.settings,
    )
    minutes_allowed = IntegerWithWarningField(
        display_name=('Minutes Allowed'),
        help=_(
            'Number of minutes allowed to finish this assessment. '
            'Set 0 for no time-limit. '
            'If there is a time-limit, the student will only be given one attempt.'
        ),
        warning=_(
            'Setting minutes allowed means that this question can only have one attempt, '
            'regardless of the value of the maximum attempts field.'
        ),
        default=0,
        scope=Scope.settings,
    )
    time_started = Date(
        help=_('time student started this assessment'),
        scope=Scope.user_state,
    )


class TimedCapaMixin(TimedCapaFields):
    def set_time_started(self):
        """
        Sets the time when the student started the module.
        """
        self.time_started = datetime.datetime.now(UTC())

    def start_problem(self, _data=None):
        """
        Called from the interstitial view, starts a timed problem if
        it hasn't already been started.

        Returns html response for the problem.
        """
        if self.is_timed_problem() and not self.time_started:
            self.set_time_started()
        return {
            'html': self.get_problem_html(encapsulate=False)
        }

    def exceeded_time_limit(self):
        """
        For a timed exam, has student used up allotted time.
        Returns false for non-timed exams.
        """
        if not self.is_timed_problem() or not self.time_started:
            return False
        now = datetime.datetime.now(UTC())
        time_limit_end = self.time_started + datetime.timedelta(minutes=(self.minutes_allowed))
        return now > time_limit_end

    def is_timed_problem(self):
        """
        Checks whether the problem is a timed exam.
        """
        return self.minutes_allowed > 0

    def get_timed_context(self, total_seconds_left, end_time_to_display):
        context = {
            'problem_is_timed': self.is_timed_problem(),
            'problem_has_finished': self.closed() or self.is_submitted(),
            'exceeded_time_limit': self.exceeded_time_limit() and not self.done,
            'seconds_before_warning': self.minutes_before_warning * 60,
            'total_seconds_left': total_seconds_left,
            'minutes_allowed': self.minutes_allowed,
            'start_time': self.time_started,
            'end_time_to_display': end_time_to_display.replace(microsecond=0),
        }
        return context
