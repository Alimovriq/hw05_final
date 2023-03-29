# Проект социальная сеть «Yatube»
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![sqlite](https://skillicons.dev/icons?i=sqlite)](https://sqlite.org/)]
[![django](https://skillicons.dev/icons?i=django)](https://https://www.djangoproject.com/)]

## Описание
 Социальная сеть с возможностью публикации записей с изображениями. Записи можно комментировать, на авторов подписываться и вступать в сообщества. Доступно восстановление пароля через почту. Настроены пагинация и кэширование. Код покрыт тестами.

## Возможности
- Регистрация пользователя / Аутентификация
- Восстановление пароля по email
- Создавать / удалять посты с изображениями
- Вставать в сообщества
- Комментировать записи

## Технологии
 - Python 3.7.13
 - Django 2.2.16
 - sorl-thumbnail 12.7.0
 - подробнее см. прилагаемый файл зависимостей requrements.txt

## Установка
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Alimovriq/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py makemigrations
```
```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Автор
Алимов Ринат
https://github.com/Alimovriq
