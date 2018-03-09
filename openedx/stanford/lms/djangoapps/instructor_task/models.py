class DeleteFileMixin(object):
    def delete_file(self, course_id, filename):
        """
        Given the `course_id` and `filename` for the report, this method deletes the report
        """
        path = self.path_to(course_id, filename)
        self.storage.delete(path)
