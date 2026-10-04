from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class QuestionModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='История')

    def test_category_creation_and_unique_name(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(self.category.name, 'История')

        duplicate = Category(name='История')
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_choice_question_requires_exactly_four_answers_and_one_correct(self):
        question = ChoiceQuestion.objects.create(category=self.category, text='Кой е първи цар на България?')

        for option in [
            ('Симеон I', True),
            ('Петър I', False),
            ('Кирил', False),
            ('Иван Шишман', False),
        ]:
            AnswerOption.objects.create(question=question, text=option[0], is_correct=option[1])

        question.full_clean()

        question2 = ChoiceQuestion(category=self.category, text='Невалиден въпрос')
        with self.assertRaises(ValidationError):
            question2.full_clean()

        question3 = ChoiceQuestion.objects.create(category=self.category, text='Друг въпрос')
        for option in [
            ('A', False),
            ('B', False),
            ('C', False),
        ]:
            AnswerOption.objects.create(question=question3, text=option[0], is_correct=option[1])
        with self.assertRaises(ValidationError):
            question3.full_clean()

        question4 = ChoiceQuestion.objects.create(category=self.category, text='Трети въпрос')
        for option in [
            ('A', True),
            ('B', True),
            ('C', False),
            ('D', False),
        ]:
            AnswerOption.objects.create(question=question4, text=option[0], is_correct=option[1])
        with self.assertRaises(ValidationError):
            question4.full_clean()

    def test_numeric_question_requires_correct_answer(self):
        question = NumericQuestion.objects.create(category=self.category, text='Колко е 12 + 8?', correct_answer=20)
        question.full_clean()

    def test_choice_question_delete_cascades_options(self):
        question = ChoiceQuestion.objects.create(category=self.category, text='Какво е 2 + 2?')
        for text in ['3', '4', '5', '6']:
            AnswerOption.objects.create(question=question, text=text, is_correct=(text == '4'))

        question.delete()
        self.assertEqual(AnswerOption.objects.count(), 0)

    def test_category_delete_is_protected_when_questions_exist(self):
        question = ChoiceQuestion.objects.create(category=self.category, text='Кой е столицата на България?')
        AnswerOption.objects.create(question=question, text='София', is_correct=True)
        AnswerOption.objects.create(question=question, text='Пловдив', is_correct=False)
        AnswerOption.objects.create(question=question, text='Варна', is_correct=False)
        AnswerOption.objects.create(question=question, text='Русе', is_correct=False)

        with self.assertRaises(Exception):
            self.category.delete()

    def test_numeric_question_creation(self):
        question = NumericQuestion.objects.create(category=self.category, text='Колко е 9 * 9?', correct_answer=81)
        self.assertEqual(question.correct_answer, 81)
