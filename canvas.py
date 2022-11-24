import os
import io
import pandas as pd
import datetime as dt

from canvasapi import Canvas
from zipfile import ZipFile
from tqdm.auto import tqdm


class CanvasConnect:
    def __init__(self, COURSE, YEAR, ASSIGNMENT, API_KEY = "canvas_api_key.txt", CANVAS = "https://canvas.vu.nl/"):
        with open(API_KEY) as file: self.canvas = Canvas(CANVAS, file.read())
        self.course = next(course for course in self.canvas.get_courses() if getattr(course, "course_code") == COURSE and getattr(course, start_at_date, dt.datetime.min).year == int(YEAR))
        self.assignment = next(assignment for assignment in self.course.get_assignments() if getattr(assignment, "name") == ASSIGNMENT)

        def _iter_students():
          for student in self.course.get_enrollments():
            if student.type == "StudentEnrollment":
              last_name, pref = student.user["sortable_name"].split(', ')
              initials, middle_name, *_ = pref.split(" ", 1) + [""]
              yield(student.user_id, 
                    student.user["login_id"], 
                    student.id, 
                    last_name,
                    middle_name,
                    initials, 
                    student.user["short_name"].replace(f" {middle_name} {last_name}", "").replace(f" {last_name}", "").strip()
                    )
          
        self.students = pd.DataFrame(_iter_students(), columns=["canvas_id", "vunet_id", "student_id", "lastname", "middlename", "initials", "firstname"]).set_index("canvas_id")

    def download_submissions(self, path_to="", no_zip=False):
        def _save_file(content, filename):
            with open(filename, 'wb') as file:
                file.write(content)
        status = {}
        for submission in tqdm(self.assignment.get_submissions()):
            if submission.missing: 
                status[submission.user_id] = "MISSING"
                continue
            if submission.late: 
                status[submission.user_id] = "LATE"
            try:
                for attachment in submission.attachments:
                    student = self.students.loc[submission.user_id]
                    response = self.assignment._requester.request("GET", _url=attachment["url"])
                    filename = attachment["display_name"]
                    filepref = "%s%s%s_%s_%s" % (student.lastname.lower().replace(' ', ''),
                                                 student.initials.replace('.', '').lower(),
                                                 student.middlename.replace(' ', '').lower(),
                                                 submission.user_id,
                                                 attachment["id"])
                    path = os.path.join(path_to, filepref)
                    if not filename.lower().endswith(".zip"):
                        _save_file(response.content, f"{path}_{filename}")
                    else:
                        zipfile = ZipFile(io.BytesIO(response.content))                
                        
                        if no_zip:
                            for file in zipfile.filelist:
                                if os.path.isfile(file.filename):
                                    _save_file(zipfile.read(file), f"{path}_{filename}")
                        else:
                            zipfile.extractall(path)
            except:
                status[submission.user_id] = "+".join((status.get(submission.user_id, ""), "FAILED_DOWNLOAD"))
        return status
        
    def post_grades(self, grades, key="canvas_id"):
        assert input("Press y(es) to confirm posting {len(grades)} grades")[0] == "y"
        failed = []
        students = self.students.reset_index().set_index(key, drop=False)["canvas_id"]
        for key, grade in tqdm(grades.items()):
            if not self.assignment.get_submission(students[key]).edit(submission={"posted_grade": str(grade)}):
                failed.append(key)
        return failed
    
    def upload_feedback(self, files, path="", key="canvas_id"):
        assert input("Press y(es) to confirm posting {len(files)} feedback files")[0] == "y"
        failed = []
        students = self.students.reset_index().set_index(key, drop=False)["canvas_id"]
        for key, file in tqdm(files.items()):
            if not self.assignment.get_submission(students[key]).upload_comment(os.path.join(path, file)):
                failed.append(key)
        return failed
        
        
if __name__ == "__main__":
    connection = CanvasConnect("XM_0051", "2021", "Assignment 1")
    connection.download_submissions()
 