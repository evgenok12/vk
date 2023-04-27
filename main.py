import os
from urllib.parse import urlsplit
import random
import requests
from environs import Env


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
    target_comic_image_extension = os.path.splitext(urlsplit(target_comic_image_url).path)[1]
    target_comic_image_path = f'comic{target_comic_image_extension}'
    with open(target_comic_image_path, 'wb') as image:
        image.write(target_comic_image_response.content)
    return target_comic_text, target_comic_image_path


def get_image_upload_url():
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'access_token': vk_access_token,
        'v': vk_api_version,
        'group_id': vk_group_id
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    payload = response.json()
    return payload['response']['upload_url']


def upload_image_to_server(upload_url, image_path):
    params = {'access_token': vk_access_token, 'v': vk_api_version}
    with open(image_path, 'rb') as comic:
        response = requests.post(upload_url, params=params, files={'photo': comic})
    response.raise_for_status()
    payload = response.json()
    return payload['server'], payload['photo'], payload['hash']


def save_image_to_album(server, photo, hash):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': vk_access_token,
        'v': vk_api_version,
        'group_id': vk_group_id,
        'server': server,
        'photo': photo,
        'hash': hash,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    payload = response.json()
    return payload['response'][0]['owner_id'], payload['response'][0]['id']


def post_comic_to_wall(owner_id, photo_id, message):
    url = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': vk_access_token,
        'v': vk_api_version,
        'owner_id': f'-{vk_group_id}',
        'from_group': 1,
        'message': message,
        'attachments': f'photo{owner_id}_{photo_id}'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    vk_access_token = env('VK_ACCESS_TOKEN')
    vk_api_version = env('VK_API_VERSION', default='5.131')
    vk_id_client = env('VK_APP_CLIENT_ID')
    vk_group_id = env('VK_GROUP_ID')
    
    print('Скрипт запущен')

    comic_text, image_path = download_random_comic()
    print('Комикс скачан в локальную директорию')

    upload_url = get_image_upload_url()
    print('URL для загрузки комикса получен')

    server_param, photo_param, hash_param = upload_image_to_server(upload_url, image_path)
    print('Комикс загружен на сервер') 

    owner_id, photo_id = save_image_to_album(server_param, photo_param, hash_param)
    print('Комикс сохранен в альбоме группы')   

    post_comic_to_wall(owner_id, photo_id, comic_text)
    print('Комикс опубликован на стене группы')

    os.remove(image_path)
    print('Комикс удален из локальной директории')
    print('Скрипт завершил работу')
