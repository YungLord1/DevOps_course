#Описание исправленных уязвимостей

При сканировании образа приложения с помощью утилиты trivy получил уязвимости от alpine 3.23.3 library zlib CVE-2026-22184(HIGH), CVE-2026-27171(MEDIUM) и 2 уязвимости от python-pkg: library pip(METADATA), CVE-2025-8869(Medium), CVE-2026-1703(LOW)

Чтобы их исправить, я выполнил следующие действия:

1. Поменял версию python-alpine с 3.12 на 3.13
2. Добавил команду RUN apk update && apk upgrade --no-cache для обновления пакетов alpine до последних версий
3. Обновил менеджер пакетов для python до последней версии: RUN pip install --upgrade pip
4. Объединил все RUN в один: RUN apk update && apk upgrade --no-cache &&  \
          pip install --no-cache-dir --upgrade pip==25.0.1 && \
          pip install --no-cache-dir .

На этом отчет хацкера закончен, спасибо за внимание! :) (◣_◢)