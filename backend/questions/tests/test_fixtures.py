from django.core.management import call_command
from django.test import TestCase


class QuestionFixtureTests(TestCase):
    fixtures = ['questions/question_bank']

    def test_fixture_has_expected_question_bank_counts(self):
        from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion

        self.assertEqual(Category.objects.count(), 6)
        self.assertEqual(ChoiceQuestion.objects.count(), 12)
        self.assertEqual(AnswerOption.objects.count(), 48)
        self.assertEqual(NumericQuestion.objects.count(), 12)

    def test_fixture_questions_are_valid(self):
        from questions.models import ChoiceQuestion, NumericQuestion

        for question in ChoiceQuestion.objects.all():
            self.assertEqual(question.answeroption_set.count(), 4)
            self.assertEqual(question.answeroption_set.filter(is_correct=True).count(), 1)

        for question in NumericQuestion.objects.all():
            self.assertIsNotNone(question.correct_answer)

    def test_fixture_loads_without_error(self):
        from questions.models import Category

        self.assertTrue(Category.objects.exists())
