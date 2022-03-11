from typing import Dict, List

from math_challenge_related.math_challenge import Challenge
from math_challenge_related.math_challenge_result import MathChallengeResult


class ResultChecker:

    def __init__(self, challenge_name_and_gold_answers_dict: Dict[str, List[str]]):
        self.challenge_name_and_gold_answers_dict = {k: v for k, v in challenge_name_and_gold_answers_dict.items() if k.startswith("MC")}
        self.challenge_name_and_gold_pretty_orig_answers_dict = {k: v for k, v in challenge_name_and_gold_answers_dict.items() if k.startswith("original")}
        self.correct_challenges_dict, self.challenge_wise_retaining = \
            Challenge.load_gold_answers(self.challenge_name_and_gold_answers_dict)

    def check_one_challenge(self, student, challenge_nm, answers_arr) -> MathChallengeResult:
        challenge = Challenge(answers=answers_arr,
                              challenge_name=challenge_nm,
                              list_of_text_retain_dict=self.challenge_wise_retaining.get(challenge_nm, {}),
                              student=student,
                              is_student_resp=True
                              )
        result: MathChallengeResult = MathChallengeResult.result(student_ans=challenge,
                                                                 correct_ans=self.correct_challenges_dict[challenge_nm],
                                                                 correct_pretty_ans=self.challenge_name_and_gold_pretty_orig_answers_dict[f"original_{challenge_nm}"]
                                                                )
        return result
