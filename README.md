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
