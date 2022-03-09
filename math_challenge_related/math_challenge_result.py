from typing import List, Dict

from math_challenge_related.math_challenge import Challenge
from math_challenge_related.student_info import StudentInfo


class MathChallengeResult:

    def __init__(self):
        self.passed: bool = False
        self.num_correct: int = 0
        self.num_wrong: int = 0
        self.diagnostics: List[str] = []
        self.student_ans: List[int] = []
        self.gold_ans: List[int] = []
        self.gold_orig_ans: List[str] = []
        self.challenge_name = ""

    @classmethod
    def result(cls, student_ans: Challenge, correct_ans: Challenge) -> "MathChallengeResult":
        assert student_ans.is_student_resp, f"Did not pass the right student response:\n{student_ans}"
        assert not correct_ans.is_student_resp, f"Did not pass the right correct response:\n{correct_ans}"
        assert len(student_ans.answers) == len(correct_ans.answers), f"Student challenge and correct challenge number of answers mismatch, cannot compare:\nstudent response: {student_ans}\ncorrect response: {correct_ans}.\n"
        assert student_ans.challenge_name == correct_ans.challenge_name, f"Student challenge and correct challenge names mismatch, cannot compare:\nstudent response: {student_ans}\ncorrect response: {correct_ans}.\n"

        r = MathChallengeResult()

        for sa, ca in zip(student_ans.answers, correct_ans.answers):
            # sometimes there can be multiple answers
            if isinstance(ca, list):
                if sa in ca:
                    r.num_correct += 1
                    r.diagnostics.append("1")
                else:
                    r.num_wrong += 1
                    r.diagnostics.append("0")
            else:
                if sa == ca:
                    r.num_correct += 1
                    r.diagnostics.append("1")
                else:
                    r.num_wrong += 1
                    r.diagnostics.append("0")

        r.passed = r.passed_as_per_grade(num_correct=r.num_correct, grade=student_ans.student.grade)
        r.challenge_name = student_ans.challenge_name
        r.student_ans = student_ans.answers
        r.gold_ans = correct_ans.answers
        r.gold_orig_ans = correct_ans.orig_answers
        return r

    @classmethod
    def passed_as_per_grade(cls, num_correct, grade):
        gradewise_threshold = {
            "Kindergarten": 3,
            "First grade": 3,
            "Second grade": 7,
            "Third grade": 7,
            "Fourth grade": 12,
            "Fifth grade": 12
        }
        return num_correct >= gradewise_threshold[grade]

    @classmethod
    def summarize(cls, results: List["MathChallengeResult"]):
        return {
            "total_num_correct": sum([r.num_correct for r in results]),
            "total_num_wrong": sum([r.num_wrong for r in results]),
            "total_num_passed": sum([1 if r.passed else 0 for r in results])
        }

    @classmethod
    def compute_student_scores(cls, student_list_challenges_dict: Dict[StudentInfo, List["Challenge"]], correct_challenges_dict: Dict[str, "Challenge"]):
        student_scores: Dict[StudentInfo, List[MathChallengeResult]] = {}
        for student, challenges_list in student_list_challenges_dict.items():
            for challenge in challenges_list:
                if challenge.student not in student_scores:
                    student_scores[student] = []
                # if we do not have correct answers for MC5, then ignore this student entry.
                if challenge.challenge_name in correct_challenges_dict:
                    student_scores[student].append(
                        MathChallengeResult.result(student_ans=challenge, correct_ans=correct_challenges_dict[challenge.challenge_name])
                    )
        return student_scores

    def __repr__(self):
        return f"{'pass' if self.passed else 'fail'}\tcorrect: {self.num_correct}, wrong: {self.num_wrong}"

    @classmethod
    def create_leaderboard(cls, student_scores: Dict[StudentInfo, List["MathChallengeResult"]]):
        return sorted(student_scores.items(), key=lambda item: MathChallengeResult.summarize(item[1])["total_num_passed"], reverse=True)
