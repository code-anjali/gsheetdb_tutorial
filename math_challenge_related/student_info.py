from math_challenge_related.utils import abbreviate_lname


class StudentInfo:
    def __init__(self, f_name:str,l_name:str,grade:str,teacher:str,email:str):
        self.email = email
        self.f_name = str.capitalize(f_name.lower().strip())
        self.l_name = str.capitalize(l_name.lower().strip())
        self.grade = grade
        self.teacher = str.capitalize(self.preprocess_teacher_name(teacher.strip()))

    @classmethod
    def preprocess_teacher_name(cls, tn):
        # Ms. Erica garl -> garl
        tn = tn.strip()
        ptn = tn.split(" ")[-1].lower()
        ptn_splits = [x.strip() for x in ptn.replace(".", " ").split(" ") if x.strip()]
        if len(ptn_splits) == 0:
            return "unknown"
        elif len(ptn_splits) == 1:
            return ptn_splits[0]

        # Ms.Garl -> garl (no space after .)
        if not ptn_splits[-1].strip():
            return ptn_splits[-2]
        else:  # Erica G. -> g
            return ptn_splits[-1]

    def get_formal_abbreviated_name(self):
        return f"{self.f_name} {abbreviate_lname(lname=self.l_name)}".strip()

    def __hash__(self):
        return hash((self.f_name, self.l_name, self.grade, self.teacher))

    def __eq__(self, other):
        return (self.f_name, self.l_name, self.grade, self.teacher) == (other.f_name, other.l_name, other.grade, other.teacher)

    def __repr__(self):
        return f"< {self.get_formal_abbreviated_name()}, {self.grade}: Ms. {self.teacher}: {self.f_name} {self.l_name}>"
