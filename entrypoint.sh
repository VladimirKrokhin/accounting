#!/bin/sh
set -e

# Применяем миграции
migrate-app

# Запускаем приложение
exec start-app
