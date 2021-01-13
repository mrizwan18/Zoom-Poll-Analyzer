class Poll:
    def __init__(self):
        self.date = ""
        self.name = ""
        self.questions = []
        self.question_list = []
        self.students = {}

    def set_name(self, name):
        self.name = name

    def set_date(self, date):
        self.date = date

    def insert_question(self, question):
        self.questions.append(question)

    def insert_student(self, name):
        self.students[name] = self.questions
        self.question_list = self.questions
        self.questions = []

    def if_student_exists(self, name):
        check = False
        students = list(self.students.keys())
        for i in range(len(students)):
            if name.lower() == students[i].lower():
                check = True
                break
        return check
