import os
from urllib.parse import urlsplit
import random
import requests
from environs import Env


def raise_for_status_vk_api(payload):
    if 'error' in payload:
        error = payload['error']
        message = (
            f"VK API Error {error['error_code']}: {error['error_msg']}"
        )
        raise requests.HTTPError(message)


def download_random_comic():
    last_comic_url = 'https://xkcd.com/info.0.json'
    last_comic_response = requests.get(last_comic_url)
    last_comic_response.raise_for_status()
    last_comic_id = last_comic_response.json()['num']
    target_comic_url = f'https://xkcd.com/{random.randint(1, last_comic_id)}/info.0.json'
    target_comic_response = requests.get(target_comic_url)
    target_comic_response.raise_for_status()
    target_comic_payload = target_comic_response.json()
    target_comic_image_url = target_comic_payload['img']
    target_comic_text = target_comic_payload['alt']
    target_comic_image_response = requests.get(target_comic_image_url)
    target_comic_image_response.raise_for_status()
    target_comic_image_extension = os.path.splitext(
        urlsplit(target_comic_image_url).path)[1]
    target_comic_image_path = f'comic{target_comic_image_extension}'
    with open(target_comic_image_path, 'wb') as image:
        image.write(target_comic_image_response.content)
    return target_comic_text, target_comic_image_path


def get_image_upload_url(access_token, api_version, group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'access_token': access_token,
        'v': api_version,
        'group_id': group_id
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    payload = response.json()
    raise_for_status_vk_api(payload)
    return payload['response']['upload_url']


def upload_image_to_server(access_token, api_version, upload_url, image_path):
    params = {'access_token': access_token, 'v': api_version}
    with open(image_path, 'rb') as comic:
        response = requests.post(
            upload_url, params=params, files={'photo': comic})
    response.raise_for_status()
    payload = response.json()
    raise_for_status_vk_api(payload)
    return payload['server'], payload['photo'], payload['hash']


def save_image_to_album(
        access_token, api_version, group_id, server_param, photo_param, hash_param):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': access_token,
        'v': api_version,
        'group_id': group_id,
        'server': server_param,
        'photo': photo_param,
        'hash': hash_param,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    payload = response.json()
    raise_for_status_vk_api(payload)
    return payload['response'][0]['owner_id'], payload['response'][0]['id']


def post_comic_to_wall(
        access_token, api_version, group_id, owner_id, photo_id, message):
    url = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': access_token,
        'v': api_version,
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'message': message,
        'attachments': f'photo{owner_id}_{photo_id}'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    payload = response.json()
    raise_for_status_vk_api(payload)


def main():
    env = Env()
    env.read_env()
    vk_access_token = env('VK_ACCESS_TOKEN')
    vk_api_version = env('VK_API_VERSION', default='5.131')
    vk_group_id = env('VK_GROUP_ID')

    print('Скрипт запущен')
    comic_text, image_path = download_random_comic()
    print('Комикс скачан в локальную директорию')

    try:
        upload_url = get_image_upload_url(
            vk_access_token, vk_api_version, vk_group_id)
        print('URL для загрузки комикса получен')
        server_param, photo_param, hash_param = upload_image_to_server(
            vk_access_token, vk_api_version, upload_url, image_path)
        print('Комикс загружен на сервер')
        owner_id, photo_id = save_image_to_album(
            vk_access_token, vk_api_version, vk_group_id, server_param, photo_param, hash_param)
        print('Комикс сохранен в альбоме группы')
        post_comic_to_wall(
            vk_access_token, vk_api_version, vk_group_id, owner_id, photo_id, comic_text)
        print('Комикс опубликован на стене группы')
    finally:
        os.remove(image_path)
        print('Комикс удален из локальной директории')

    print('Скрипт успешно завершил работу')


if __name__ == '__main__':
    main()
