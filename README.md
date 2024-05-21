# api_yamdb
Проект **YaMDb** собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку. Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число). Из пользовательских оценок формируется усреднённая оценка произведения — рейтинг.

## Как запустить проект

### Клонировать репозиторий и перейти в него в командной строке:

```sh
git clone git@github.com:OverDrive13/api_yamdb.git
cd api_yamdb
```

### Создать и активировать виртуальное окружение:

python3 -m venv env
source env/bin/activate

###  Установить зависимости из файла requirements.txt:
```sh
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
### Выполнить миграции:
```sh
python3 manage.py migrate
```
### Запустить проект:
```sh
python3 manage.py runserver
```

##  Примеры запросов

###  Получение списка всех категорий

```
GET /api/v1/categories/
```

Response:

{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "name": "string",
      "slug": "^-$"
    }
  ]
}



### Добавление новой категории
```
POST /api/v1/categories/
```

Response:

{
  "name": "string",
  "slug": "string"
}

# Использованные технологии

Django,  Django REST Framework


# Авторы
Антон Лисица
Александр Толстиков
Марина Асташова