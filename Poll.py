import unicodedata


class Poll:
    def __init__(self):
        self.date = ""
        self.name = ""
        self.questions = []
        self.question_list = []
        self.students = {}
        self.answerkey = []
        self.marked = []
        self.selected_options = []

    def strip_accents(self, text):
        choices = {"İ": "I", "Ş": "S", "Ü": "U", "Ö": "O", "Ç": "C", "Ğ": "G", "i": "i", "ç": "c", "ğ": "g", "ö": "o",
                   "ş": "s", "ü": "u"}
        for i in range(len(text)):
            text = text.replace(text[i:i + 1], choices.get(text[i], text[i]))
        return ''.join(char for char in
                       unicodedata.normalize('NFKD', text)
                       if unicodedata.category(char) != 'Mn')

    def set_name(self, name):
        self.name = name

    def set_date(self, date):
        self.date = date

    def insert_question(self, question):
        self.questions.append(question)

    def insert_student(self, name):
        self.students[self.strip_accents(name)] = self.questions
        self.question_list = self.questions
        self.questions = []

    def if_student_exists(self, name):
        check = False
        students = list(self.students.keys())
        for i in range(len(students)):
            if self.strip_accents(students[i].lower()) in self.strip_accents(name.lower()):
                check = True
                break
        return check
