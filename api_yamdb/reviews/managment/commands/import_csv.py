import csv

from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    """Команда для заполнения базы данных."""

    def handle(self, *args, **options):
        """Обработка команды."""
        with open('./static/data/users.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not User.objects.exists():
                for row in reader:
                    User.objects.create(
                        username=row['username'],
                        email=row['email'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        role=row['role'],
                        bio=row['bio'],
                    )
                print('Данные успешно загружены.')
            else:
                print('Данные уже загружены.')

        with open('./static/data/categories.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not Category.objects.exists():
                for row in reader:
                    Category.objects.create(
                        name=row['name'],
                        slug=row['slug'],
                    )
                print('Категории загружены.')
            else:
                print('Категории уже загружены.')

        with open('./static/data/genres.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not Genre.objects.exists():
                for row in reader:
                    Genre.objects.create(
                        name=row['name'],
                        slug=row['slug'],
                    )
                print('Жанры загружены.')
            else:
                print('Жанры уже загружены.')

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
            if Title.objects.exists():
                print('Фильмы загружены.')

        with open('./static/data/reviews.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not Review.objects.exists():
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
                print('Отзывы загружены.')
            else:
                print('Отзывы уже загружены.')

        with open('./static/data/comments.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not Comment.objects.exists():
                for row in reader:
                    author = User.objects.get(username=row['author'])
                    review = Review.objects.get(id=row['review_id'])
                    Comment.objects.create(
                        review=review,
                        text=row['text'],
                        author=author,
                        pub_date=row['pub_date'],
                    )
                print('Комментарии загружены.')
            else:
                print('Комментарии уже загружены.')
