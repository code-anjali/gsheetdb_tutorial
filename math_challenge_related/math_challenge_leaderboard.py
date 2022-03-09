# student info, make a class and read from csv; pre-process teacher name
# list of student answers : read from csv,  make a challenge class (correct_ans, challenge_name); make a challengeResponse (student_ans) and pre-process;; ((make a list of challenge that holds all challenges))
# list of correct answers : read from csv
# give pass/fail and score based on grade : create result object and compare a1, a2 and maintain a grade wise map
from typing import List, Tuple

from prettytable import PrettyTable

from math_challenge_related.math_challenge import Challenge
from math_challenge_related.math_challenge_result import MathChallengeResult
from math_challenge_related.student_info import StudentInfo


def main(correct_answers_fp, student_answers_fp, diagnostics_for_mc_challenge: str) -> (PrettyTable, PrettyTable):
    diagnostics_for_mc_challenge = diagnostics_for_mc_challenge.upper().strip()  # mc2 -> MC2
    correct_challenges_dict, challenge_wise_retaining = Challenge.load_gold_answers(fp=correct_answers_fp)
    student_challenges_list_dict = Challenge.load_student_answers(fp=student_answers_fp, challenge_wise_retaining=challenge_wise_retaining)
    student_scores = MathChallengeResult.compute_student_scores(correct_challenges_dict=correct_challenges_dict, student_list_challenges_dict=student_challenges_list_dict)
    leaderboard: List[Tuple[StudentInfo, List["MathChallengeResult"]]] = MathChallengeResult.create_leaderboard(student_scores=student_scores)


    gold_ans = correct_challenges_dict[diagnostics_for_mc_challenge].answers
    # diagnostics = ["", *gold_ans]
    tab = '\t'
    dp = PrettyTable()
    dp.field_names = ["student name", *[f"A{(x+1)}: {gold_ans[x]}" for x in range(18)]]
    dp.align['student name'] = 'l'
    for student_entry in leaderboard:
        student_info = student_entry[0]
        challenge_result = [(x.diagnostics, x.student_ans) for x in student_entry[1] if x.challenge_name == diagnostics_for_mc_challenge]
        challenge_result = challenge_result[0] if len(challenge_result) == 1 else None
        if challenge_result:
            diagnostics=[]
            for judgment, pred in zip(challenge_result[0], challenge_result[1]):
                diagnostics.append(f'{pred}: {judgment}')
            dp.add_row([student_info, *diagnostics])


    print(f"\n\nLeaderboard")
    p = PrettyTable()
    p.field_names = ["student name", "points", "grade", "student info", "ignore_this_minus_points", 'successful submissions', 'num correct']
    for (student, list_results) in leaderboard:
        total_pass = MathChallengeResult.summarize(list_results)['total_num_passed']
        total_correct = MathChallengeResult.summarize(list_results)['total_num_correct']
        p.add_row([student.get_formal_abbreviated_name(),  100* int(total_pass), student.grade, student.__repr__(), -100* int(total_pass), total_pass, total_correct])
    p.reversesort = False
    p.sortby = "ignore_this_minus_points"
    p.align['student info'] = 'l'
    print(p)
    print("\n")
    print(dp)
    return p, dp


if __name__ == '__main__':
    main(correct_answers_fp="data/uploaded/correct_answers.csv", student_answers_fp="data/uploaded/student-answers-withduplicates.csv", diagnostics_for_mc_challenge="MC2")
