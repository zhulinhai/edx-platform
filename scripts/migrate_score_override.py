#!/usr/bin/env python
"""
Script to update old score overrides to match upstream overrides.
"""
import datetime
import itertools
import os
import django
from django.db import transaction
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.monkey_patch import django_db_models_options


def main():
    from django.contrib.auth.models import User
    from openassessment.assessment.models import Assessment, AssessmentPart, StaffWorkflow
    from openassessment.workflow.models import AssessmentWorkflow, AssessmentWorkflowStep
    from student.models import anonymous_id_for_user, user_by_anonymous_id
    from submissions.models import Score, ScoreSummary, ScoreAnnotation

    old_scores = Score.objects.filter(submission__isnull=True, reset=False).order_by('id')
    updated_count = 0
    for score in old_scores:
        try:
            with transaction.atomic():
                # ScoreSummary is updated on Score saves but for this script we don't want that.
                # Correct way is to disconnect post_save signal, but since the receiver function
                # is defined in the class, we can't reference it. Workaround here is to just
                # prefetch the score summary and resave it to maintain its original field values.
                score_summary = ScoreSummary.objects.get(student_item=score.student_item)

                # Update old override with submission from the score preceding it
                submission = Score.objects.filter(
                    student_item=score.student_item,
                    created_at__lte=score.created_at,
                    submission__isnull=False,
                ).order_by('-created_at')[:1].get().submission
                score.submission = submission
                score.save()

                # Offset override reset by 1 second for convenience when sorting db
                override_date = score.created_at - datetime.timedelta(seconds=1)
                # Create reset score
                Score.objects.create(
                    student_item=score.student_item,
                    submission=None,
                    points_earned=0,
                    points_possible=0,
                    created_at=override_date,
                    reset=True,
                )

                # Restore original score summary values
                score_summary.save()

                # Fetch staff id from score course for ScoreAnnotation
                course_id = CourseKey.from_string(score.student_item.course_id)
                staff = User.objects.filter(
                    courseaccessrole__role__in=['instructor', 'staff'],
                    courseaccessrole__course_id=course_id,
                )[:1].get()
                staff_id = anonymous_id_for_user(staff, course_id, save=False)

                # Create ScoreAnnotation
                score_annotation = ScoreAnnotation(
                    score=score,
                    annotation_type="staff_defined",
                    creator=staff_id,
                    reason="A staff member has defined the score for this submission",
                )
                score_annotation.save()

                # ORA2 Table Updates...
                # Fetch rubric from an existing assessment
                assessment = Assessment.objects.filter(submission_uuid=submission.uuid)[:1].get()
                rubric = assessment.rubric

                staff_assessment = Assessment.create(
                    rubric=rubric,
                    scorer_id=staff_id,
                    submission_uuid=submission.uuid,
                    score_type="ST",
                    scored_at=override_date,
                )

                # Fake criterion selections
                rubric_index = rubric.index
                assessment_parts = []

                criteria_without_options = rubric_index.find_criteria_without_options()
                criteria_with_options = set(rubric_index._criteria_index.values()) - criteria_without_options
                ordered_criteria = sorted(criteria_with_options, key=lambda criterion: criterion.order_num)
                criteria_options = [c.options.all() for c in ordered_criteria]
                # Just take the first combination of options which add up to the override point score
                for selection in itertools.product(*criteria_options):
                    total = sum(option.points for option in selection)
                    if total == score.points_earned:
                        for option in selection:
                            assessment_parts.append({
                                'criterion': option.criterion,
                                'option': option
                            })
                        break

                # Default to first option for each criteria if no matching sum found
                if not assessment_parts:
                    print "NO CLEAN SUM FOR SUBMISSION " + submission.uuid
                    for options in criteria_options:
                        assessment_parts.append({
                            'criterion': options[0].criterion,
                            'option': options[0],
                        })

                # Add feedback-only criteria
                for criterion in criteria_without_options:
                    assessment_parts.append({
                        'criterion': criterion,
                        'option': None
                    })

                AssessmentPart.objects.bulk_create([
                    AssessmentPart(
                        assessment=staff_assessment,
                        criterion=assessment_part['criterion'],
                        option=assessment_part['option'],
                        feedback=u""
                    )
                    for assessment_part in assessment_parts
                ])

                try:
                    staff_workflow = StaffWorkflow.objects.get(submission_uuid=submission.uuid)
                    staff_workflow.assessment = staff_assessment.id
                    staff_workflow.grading_completed_at = override_date
                except StaffWorkflow.DoesNotExist:
                    staff_workflow = StaffWorkflow(
                        scorer_id=staff_id,
                        course_id=score.student_item.course_id,
                        item_id=score.student_item.item_id,
                        submission_uuid=submission.uuid,
                        created_at=override_date,
                        grading_completed_at=override_date,
                        assessment=staff_assessment.id,
                    )
                staff_workflow.save()

                workflow = AssessmentWorkflow.get_by_submission_uuid(submission.uuid)
                try:
                    staff_step = workflow.steps.get(name='staff')
                    staff_step.assessment_completed_at = score.created_at
                    staff_step.submitter_completed_at = score.created_at
                    staff_step.save()
                except AssessmentWorkflowStep.DoesNotExist:
                    for step in workflow.steps.all():
                        step.assessment_completed_at = score.created_at
                        step.submitter_completed_at = score.created_at
                        step.order_num += 1
                        step.save()
                    workflow.steps.add(
                        AssessmentWorkflowStep(
                            name='staff',
                            order_num=0,
                            assessment_completed_at=score.created_at,
                            submitter_completed_at=score.created_at,
                        )
                    )

                # Update workflow status to done if it wasn't subsequently cancelled
                if workflow.status != 'cancelled':
                    workflow.status = 'done'
                    workflow.save()

            updated_count += 1
            user = user_by_anonymous_id(score.student_item.student_id)
            print(
                "Successfully updated score {} for user {} with email {} in course {} for item: {}".format(
                    score.id,
                    user.username,
                    user.email,
                    score.student_item.course_id,
                    score.student_item.item_id,
                )
            )
        except Exception as err:
            print("An error occurred updating score {}: {}".format(score.id, err))
            print("Please update this score manually and retry script.")
            break

    print("Script finished, number of scores updated: {}.".format(updated_count))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'openedx.stanford.lms.envs.aws')
    os.environ.setdefault("SERVICE_VARIANT", 'lms')

    django_db_models_options.patch()
    django.setup()
    main()
