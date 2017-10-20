#!/usr/bin/env python
"""
Script to fix workflows with truncated course_ids from https://github.com/Stanford-Online/edx-ora2/pull/25.
AIClassifierSet, AIGradingWorkflow and AITrainingWorkflow excluded as they are not used by Stanford.
"""
from itertools import chain
import os
import django
from django.db.models.functions import Length
from openedx.core.djangoapps.monkey_patch import django_db_models_options


def main():
    from openassessment.assessment.models import PeerWorkflow, StaffWorkflow, StudentTrainingWorkflow
    from openassessment.workflow.models import AssessmentWorkflow

    peer_workflows = PeerWorkflow.objects.annotate(course_id_len=Length('course_id')).filter(course_id_len=40)
    staff_workflows = StaffWorkflow.objects.annotate(course_id_len=Length('course_id')).filter(course_id_len=40)
    training_workflows = StudentTrainingWorkflow.objects.annotate(course_id_len=Length('course_id')).filter(course_id_len=40)

    full_course_ids = {}  # Keep local dict to avoid repeated database hits for the same course_id
    for workflow in chain(peer_workflows, staff_workflows, training_workflows):
        truncated_course = workflow.course_id
        if truncated_course not in full_course_ids:
            # Get full course_id from AssessmentWorkflow table
            try:
                assessment_workflow = AssessmentWorkflow.objects.filter(course_id__startswith=truncated_course)[:1].get()
                full_course_ids[truncated_course] = assessment_workflow.course_id
            except AssessmentWorkflow.DoesNotExist:
                print("No assessment workflow matching truncated course_id: {}".format(truncated_course))
                continue

        workflow.course_id = full_course_ids[truncated_course]
        workflow.save()

    print("Script finished.")


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'openedx.stanford.lms.envs.aws')
    os.environ.setdefault("SERVICE_VARIANT", 'lms')

    django_db_models_options.patch()
    django.setup()
    main()
