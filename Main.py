import glob
import unicodedata

import matplotlib.pyplot as plt
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
                st = Student(cleaned_row[2], strip_accents(cleaned_row[3]), strip_accents(cleaned_row[4]), exp)
                students.append(st)
            if np.isin("Öğrenci No", cleaned_row):
                start = True

    return students


def strip_accents(text):
    choices = {"İ": "I", "ı": "I", "Ş": "S", "Ü": "U", "Ö": "O", "Ç": "C", "Ğ": "G", "i": "i", "ç": "c", "ğ": "g",
               "ö": "o",
               "ş": "s", "ü": "u"}
    for i in range(len(text)):
        text = text.replace(text[i:i + 1], choices.get(text[i], text[i]))
    return ''.join(char for char in
                   unicodedata.normalize('NFKD', text)
                   if unicodedata.category(char) != 'Mn')


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
            poll.insert_student(strip_accents(tup[1]))
        polls.append(poll)
        count += 1
    return polls


def identify_poll(polls, answer_keys):
    return_polls = []
    for pl in polls:
        for ak in answer_keys:
            if ak.is_question_present(pl.question_list):
                pl.name = ak.name
                pl.answerkey = ak
                return_polls.append(pl)
                break
    return return_polls


def mark_attendance(students, polls):
    for st in students:
        for pl in polls:
            if pl.if_student_exists(st.fname + " " + st.lname):
                st.attended_polls += 1
    return students


def mark_quiz(poll):
    students = poll.students
    answer_key = poll.answerkey
    marked_students = []
    chosen_answers = {}
    for st in students:
        marks = []
        question_list = students[st]
        for q in question_list:
            if q.get_answer() in chosen_answers:
                chosen_answers[q.get_answer()] += 1
            else:
                chosen_answers[q.get_answer()] = 1
            if answer_key.get_answer(str(q.question)) == q.get_answer():
                marks.append(1)
            else:
                marks.append(0)
        marked_students.append(marks)
    return marked_students, chosen_answers


Output_folder = "output"
results = []
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
df.to_excel(Output_folder + '/attendance.xlsx', header=True, index=False)

marked_polls = []
chosen_answers = []
for poll in new_polls:
    marks, ans = mark_quiz(poll)
    poll.marked = marks
    marked_polls.append(poll)
    chosen_answers.append(ans)

poll_number = 0
for pl in marked_polls:
    questions_dict = {}
    false_indices = []
    bad_index = 0
    q_ids = []
    q_fnames = []
    q_lnames = []
    q_exps = []
    number_of_q = []
    success_rate = []
    success_per = []
    count = 0
    for st in pl.students:
        check = False
        for i in range(len(pl.students)):
            n = fnames[i].lower() + " " + lnames[i].lower()
            if strip_accents(st.lower()) in strip_accents(n):
                q_ids.append(ids[i])
                q_fnames.append(fnames[i])
                q_lnames.append(lnames[i])
                q_exps.append(exps[i])
                check = True
                break
        if not check:
            false_indices.append(bad_index)
            q_ids.append("-")
            q_fnames.append(st)
            q_lnames.append("-")
            q_exps.append("-")
        bad_index += 1
        correct = [x for x in pl.marked[count] if x == 1]
        success_rate.append("{} of {}".format(len(correct), len(pl.question_list)))
        success_per.append("Success Percentage= {} ".format((len(correct) / len(pl.question_list)) * 100))
        count += 1

    questions_dict['Öğrenci No'] = q_ids
    questions_dict['Adı'] = q_fnames
    questions_dict['Soyadı'] = q_lnames
    questions_dict['Açıklama'] = q_exps
    poll_name = pl.name

    # print("for poll # {}, ".format(poll_number + 1), chosen_answers[poll_number])
    # colors = []
    # for value in chosen_answers[poll_number].keys():  # keys are the names of the boys
    #     if pl.answerkey == value:
    #         colors.append('g')
    #     else:
    #         colors.append('b')
    plt.bar(list(chosen_answers[poll_number].keys()), chosen_answers[poll_number].values(), color="g")
    plt.title(poll_name)
    plt.savefig(Output_folder + "/" + poll_name + str(poll_number))
    plt.clf()

    for i in range(len(pl.question_list)):
        col = []
        question_number = "Q{}".format(i + 1)
        q = 0
        for m in pl.marked:
            if i >= len(m) or q in false_indices:
                col.append("-")
            else:
                col.append(m[i])
            q += 1
        questions_dict[question_number] = col

    for index in range(len(pl.students)):
        if index in false_indices:
            success_rate[index] = "-"
            success_per[index] = "-"
            number_of_q.append("-")
        else:
            number_of_q.append(len(pl.question_list))
    questions_dict['Number of Questions'] = number_of_q
    questions_dict['Success rate'] = success_rate
    questions_dict['Success Percentage'] = success_per

    results.append(questions_dict)
    df = pandas.DataFrame.from_dict(
        questions_dict)
    df.to_excel(Output_folder + "/" + poll_name + ".xlsx", header=True, index=False)
    poll_number += 1
