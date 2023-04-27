# Публикация комиксов
Скачивает рандомный комикс с [xkcd.com](https://xkcd.com) и публикует его в выбранной группе [ВКонтакте](https://vk.com)

## Зависимости
Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:

```bash
pip install -r requirements.txt
```

## Переменные окружения
- VK_APP_CLIENT_ID
- VK_ACCESS_TOKEN
- VK_GROUP_ID
- VK_API_VERSION=5.131

1. Поместите файл `.env` рядом со скриптами.
2. `.env` должен содержать текстовые данные без кавычек.

Например, если вы распечатаете содержимое `.env`, то увидите:

```bash
$ cat .env
VK_APP_CLIENT_ID=123
VK_ACCESS_TOKEN=abc123
VK_GROUP_ID=321
VK_API_VERSION=5.131
```

### Как получить `VK_APP_CLIENT_ID`
Создайте приложение на [странице для разработчиков](https://vk.com/dev) в разделе “Мои приложения”. Ссылка на него в шапке страницы.
Если нажать на кнопку “Редактировать” для нового приложения, в адресной строке вы увидите его client_id. Это и есть VK_APP_CLIENT_ID

### Как получить `VK_ACCESS_TOKEN`
Воспользуйтесь сервисов [vkhost.github.io](https://vkhost.github.io). VK_ACCESS_TOKEN – это access_token
Для работы скрипта нужные следующие права:
* Фотографии
* Стена
* Группы
* Доступ в любое время

### Как получить `VK_GROUP_ID`
Это id группы, в которой вы хотите сделать публикацию. Что узнать id можно использовать сервис [regvk.com](https://regvk.com/id/)

### Как получить `VK_API_VERSION`
Это используемая версия VK API. Дефолтное значение – 5.131. С версиями API можно озакомиться [здесь](https://vk.com/dev/versions)

## Как запустить
Запуск на Linux(Python 3) или Windows:

```bash
$ python main.py
```
Вы увидите:

```
Скрипт запущен
Комикс скачан в локальную директорию
URL для загрузки комикса получен
Комикс загружен на сервер
Комикс сохранен в альбоме группы
Комикс опубликован на стене группы
Комикс удален из локальной директории
Скрипт завершил работу
```

### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).