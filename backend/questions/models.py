from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class BaseQuestion(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='%(class)ss',
    )
    text = models.TextField()

    class Meta:
        abstract = True


class ChoiceQuestion(BaseQuestion):
    def clean(self):
        super().clean()

        if not self.pk:
            raise ValidationError({'__all__': 'Choice questions must already exist before validating answer options.'})

        options = self.answeroption_set.all()

        if len(options) != 4:
            raise ValidationError({'answeroption_set': 'Choice questions must have exactly four answer options.'})

        if options.filter(is_correct=True).count() != 1:
            raise ValidationError({'answeroption_set': 'Choice questions must have exactly one correct answer.'})

    def __str__(self):
        return self.text


class NumericQuestion(BaseQuestion):
    correct_answer = models.IntegerField()

    def __str__(self):
        return self.text


class AnswerOption(models.Model):
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        related_name='answeroption_set',
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        if not self.text.strip():
            raise ValidationError({'text': 'Answer text cannot be empty.'})

    def __str__(self):
        return self.text
