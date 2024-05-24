import csv

from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    """Команда для заполнения базы данных."""

    def handle(self, *args, **options):
        """Обработка команды."""
        with open('./static/data/users.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                User.objects.create(
                    username=row['username'],
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    role=row['role'],
                    bio=row['bio'],
                )
            if User.objects.exists():
                print('данные уже загружены.')

        with open('./static/data/categories.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.create(
                    name=row['name'],
                    slug=row['slug'],
                )
            if Category.objects.exists():
                print('данные уже загружены.')

        with open('./static/data/genres.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.create(
                    name=row['name'],
                    slug=row['slug'],
                )
            if Genre.objects.exists():
                print('данные уже загружены.')

        with open('./static/data/titles.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = Category.objects.get(slug=row['category'])
                title = Title.objects.create(
                    name=row['name'],
                    year=row['year'],
                    category=category,
                )
                for genre_slug in row['genre'].split(','):
                    genre = Genre.objects.get(slug=genre_slug)
                    title.genre.add(genre)
                if Genre.objects.exists():
                    print('данные уже загружены.')

        with open('./static/data/reviews.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                author = User.objects.get(username=row['author'])
                title = Title.objects.get(id=row['title_id'])
                Review.objects.create(
                    title=title,
                    text=row['text'],
                    author=author,
                    score=row['score'],
                    pub_date=row['pub_date'],
                )
            if Review.objects.exists():
                print('данные уже загружены.')

        with open('./static/data/comments.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                author = User.objects.get(username=row['author'])
                review = Review.objects.get(id=row['review_id'])
                Comment.objects.create(
                    review=review,
                    text=row['text'],
                    author=author,
                    pub_date=row['pub_date'],
                )
            if Comment.objects.exists():
                print('данные уже загружены.')
