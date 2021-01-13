import glob

import numpy as np
import pandas

from Answerkey import Answerkey
from Poll import Poll
from Question import Question
from Student import Student


def populate_answer_keys(directory):
    count = 1
    answer_keys = []
    for file_name in glob.iglob('{}/*.csv'.format(directory), recursive=True):
        cols = []
        df = pandas.read_csv(file_name)
        for col in df.columns:
            cols.append(col)
        answer_key = Answerkey(cols[0])
        for i, j in df.iterrows():
            answer_key.insert_question(j[0], j[1])
        answer_keys.append(answer_key)
        count += 1
    return answer_keys


def populate_students_list(directory):
    students = []
    for file_name in glob.iglob('{}/*.xls'.format(directory), recursive=True):
        start = False
        df = pandas.read_excel(file_name)
        for i in df.itertuples():
            arr = np.asarray(i)
            cleaned_row = np.asarray([x for x in arr if str(x) != 'nan'])
            if cleaned_row.size < 2:
                start = False
            if start:
                if cleaned_row.size < 6:
                    exp = " "
                else:
                    exp = cleaned_row[5]
                st = Student(cleaned_row[2], cleaned_row[3], cleaned_row[4], exp)
                students.append(st)
            if np.isin("Öğrenci No", cleaned_row):
                start = True

    return students


def populate_polls(directory):
    count = 1
    polls = []
    for file_name in glob.iglob('{}/*.csv'.format(directory), recursive=True):
        df = pandas.read_csv(file_name)
        poll = Poll()
        for i in df.itertuples():
            if len(i[0]) > 3:
                data = [np.asarray(i[0])]
                for j in range(1, len(i)):
                    if str(i[j]) != "nan":
                        data.append(i[j])
                tup = []
                for obj in data[0]:
                    tup.append(obj)
            else:
                tup = [i[0][0], i[0][1]]
            for index in range(1, len(i)):
                tup.append(i[index])
            tup = np.asarray([x for x in tup if str(x) != 'nan'])
            if poll.if_student_exists(tup[1]):
                polls.append(poll)
                poll = Poll()
            for q in range(4, len(tup), 2):
                question = Question(tup[q], tup[q + 1])
                poll.insert_question(question)
            poll.insert_student(tup[1])
        polls.append(poll)
        count += 1
    return polls


def identify_poll(polls, answer_keys):
    return_polls = []
    for pl in polls:
        for ak in answer_keys:
            if ak.is_question_present(pl.question_list):
                pl.name = ak.name
                return_polls.append(pl)
                break
    return return_polls


def mark_attendance(students, polls):
    for st in students:
        for pl in polls:
            if pl.if_student_exists(st.fname + " " + st.lname):
                st.attended_polls += 1
    return students


answer_keys = populate_answer_keys("answer-keys-directory")
student_list = populate_students_list("students-list-directory")
polls = populate_polls("polls-directory")

new_polls = identify_poll(polls, answer_keys)

marked_students = mark_attendance(student_list, new_polls)

ids = []
fnames = []
lnames = []
exps = []
att_polls = []
att_rate = []
att_per = []
for st in marked_students:
    ids.append(st.id)
    fnames.append(st.fname)
    lnames.append(st.lname)
    exps.append(st.exp)
    att_polls.append(len(new_polls))
    att_rate.append("Attended {} of {}".format(st.attended_polls, len(new_polls)))
    att_per.append("Attended Percentage = {}".format((st.attended_polls / len(new_polls)) * 100))

df = pandas.DataFrame.from_dict(
    {'Öğrenci No': ids, 'Adı': fnames, 'Soyadı': lnames, 'Açıklama': exps, 'Number of Attendance Polls': att_polls,
     'Attendance Rate': att_rate, 'Attendance Percentage': att_per})
df.to_excel('attendance.xlsx', header=True, index=False)
