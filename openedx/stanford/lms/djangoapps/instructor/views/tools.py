import csv
import json


def generate_course_forums_d3(url_handle):
    """
    Grab the csv file at url_handle and parse it

    Return a new-line joined csv string to be graphed
    """
    reader = csv.reader(url_handle)
    reader.next()
    previous_date = -1
    previous = None
    rows = [['Date', 'New Threads', 'Responses', 'Comments']]
    for row in reader:
        # This is for backward compatibility because there is a variable number of columns.
        # We only want the first 3.
        date, comment_type, number = row[0:3]
        if date != previous_date:
            if previous:
                rows.append([previous_date] + previous)
            previous = ['0', '0', '0']
            previous_date = date
        if comment_type == 'CommentThread':
            previous[0] = number
        elif comment_type == 'Response':
            previous[1] = number
        elif comment_type == 'Comment':
            previous[2] = number
    if not previous:
        return None
    else:
        rows.append([previous_date] + previous)
        csv_string = '\n'.join([
            ','.join(row)
            for row in rows
        ])
        return csv_string


def parse_student_data(student_data):
    """
    Parses student data to output a more easily-readable version of the 'state',
    which includes last submission time, number of attempts, and
    the students' answers for a specific problem.
    We have 2 cases:
        1) for students with field 'student_answers',
           we output all the fields as they are
           (maintaining JSON format if applicable)
        2) for students with field 'student_answer' (note singular),
           we only output columns for student username and that answer

    :param student_data: dict with 2 keys: 'username' and state'.
        The value of 'state' is a string version of a dict

    :return: 2-d array, where a row is the username and state data for a student.
        First row is the headers.
        Only includes students that have submitted an answer to the problem
    """
    header = ['username', 'state']
    rows = []
    for student in student_data:
        state = student['state']
        row = [student['username']]
        try:
            student_data_dict = json.loads(state)
        except ValueError:
            row_field = state
        else:
            row_field = student_data_dict.get('student_answer', state)
        row.append(row_field)
        rows.append(row)
    return header, rows


def reverse_ora2_responses(course, endpoint, include_email):
    course_id = course.id.to_deprecated_string()
    url = reverse(
        endpoint,
        kwargs={
            'course_id': course_id,
            'include_email': include_email,
        },
    )
    return url
