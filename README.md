## Виртуальная среда разработки
```py -m venv .venv```

## Установка зависимостей
```pip install -r requirements.txt```

## Предзапуск
```py manage.py collectstatic```

```py manage.py migrate```

```py manage.py createsuperuser```

## Запуск проект
- Локально 
```py manage.py runserver```

- Докер 
```docker-compose up```