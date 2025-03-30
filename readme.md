# Audio Upload Service with Yandex OAuth

## Настройка и Запуск

1. **Создайте и настройте файл `.env`:**
    ***Необходимые поля***
    * POSTGRES_SERVER
    * POSTGRES_PORT
    * POSTGRES_USER
    * POSTGRES_PASSWORD
    * POSTGRES_DB
    * SECRET_KEY
    * ALGORITHM=HS256
    * ACCESS_TOKEN_EXPIRE_MINUTES
    * REFRESH_TOKEN_EXPIRE_DAYS
    * YANDEX_CLIENT_ID
    * YANDEX_CLIENT_SECRET
    * YANDEX_REDIRECT_URI
    * FIRST_SUPERUSER_YANDEX_ID
    * API_V1_STR=/api/v1
    * UPLOADS_DIR=./uploads

2**Соберите и запустите контейнеры с помощью Docker Compose:**
 ***```docker-compose up --build```***