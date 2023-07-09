
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

## Учебный проект - Яндекс.Практика - Yatube
Yatube - социальная сеть блогеров. Функционал проекта позволяет регистрировать и авторизовать пользователей.  Писать посты и публиковать их в отдельные группы, оставлять комментарии к записям других авторов, подписываться на других авторов.

## **Установка**
Клонируем репозиторий:
```python
git@github.com:Maksim1301/hw05_final.git
```
Cоздать и активировать виртуальное окружение:

```python
python -m venv venv
```
```python
source venv/Scripts/activate
```
```python
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```python
pip install -r requirements.txt
```
Выполнить миграции:
```python
python manage.py migrate
```
Создаем супер пользователя:
```python
python manage.py createsuperuser
```
Запустить проект:
```python
python manage.py runserver
```
