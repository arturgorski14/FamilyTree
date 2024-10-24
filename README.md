# Usefull commands

## create new project
- django-admin startproject <project_name>

## create new app
- django-admin startapp <app_name>

## run development server
- py manage.py runserver

## create migration (change models first)
- py manage.py makemigrations <table>

## apply migration
- py manage.py migrate

## display executed sql on migration
- py manage.py sqlmigrate <table> <migration_number>

## interactive shell
- py manage.py shell

## checks for any problems inside a project
- py manage.py check

## more useful commands
- https://docs.djangoproject.com/en/5.1/ref/django-admin/

## pytest has been set up to run tests simply use
- pytest