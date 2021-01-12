import glob

import pandas

from Answerkey import Answerkey


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


answer_keys = populate_answer_keys("answer-keys-directory")
