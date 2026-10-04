# Quiz Conquest

## Backend

The backend is built with Django.

### Load the question bank

From the project root, run:

```bash
python backend/manage.py loaddata questions/question_bank.json
```

### Run backend tests

```bash
python backend/manage.py test questions
```
