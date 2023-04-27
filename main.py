import os
from urllib.parse import urlsplit
from pathlib import Path
import random
import requests
from environs import Env


def get_extension(url):
    return os.path.splitext(urlsplit(url).path)[1]


def download_image(url, path, image_name):
    Path(path).mkdir(parents=True, exist_ok=True)
    image_response = requests.get(url)
    image_response.raise_for_status()
    extension = get_extension(url)
    with open(f'{os.path.join(path, image_name)}{extension}', 'wb') as image:
        image.write(image_response.content)


def get_random_comics_image_url_and_text():
    last_comics_url = 'https://xkcd.com/info.0.json'
    last_comics_response = requests.get(last_comics_url)
    last_comics_response.raise_for_status()
    last_comics_id = last_comics_response.json()['num']
    target_comics_url = f'https://xkcd.com/{random.randint(1, last_comics_id)}/info.0.json'
    target_comics_response = requests.get(target_comics_url)
    target_comics_response.raise_for_status()
    target_comics_payload = target_comics_response.json()
    target_comics_image_url = target_comics_payload['img']
    target_comics_text = target_comics_payload['alt']
    return target_comics_image_url, target_comics_text


def add_required_params(params=None):
    required_params = {'access_token': vk_access_token, 'v': vk_api_version}
    if params is None:
        return required_params
    return params | required_params


def post_request_vk_api(method, additional_params=None, files=None):
    url = f'https://api.vk.com/method/{method}'
    params = add_required_params(additional_params)
    response = requests.post(url, params=params, files=files)
    response.raise_for_status()
    return response


def get_request_vk_api(method, additional_params):
    url = f'https://api.vk.com/method/{method}'
    params = add_required_params(additional_params)
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response


if __name__ == '__main__':
    env = Env()
    env.read_env()
    vk_access_token = env('VK_ACCESS_TOKEN')
    vk_api_version = env('VK_API_VERSION', default='5.131')
    vk_id_client = env('VK_APP_CLIENT_ID')
    vk_group_id = env('VK_GROUP_ID')
    
    print('Скрипт запущен')
    comics_image_url, comics_text = get_random_comics_image_url_and_text()
    comics_extension = get_extension(comics_image_url)
    download_image(comics_image_url, '', 'comics')
    print('Комикс скачан в локальную директорию')

    get_wall_upload_server_payload = get_request_vk_api(
        'photos.getWallUploadServer',
        {'group_id': vk_group_id}
        ).json()
    upload_url = get_wall_upload_server_payload['response']['upload_url']
    print('URL для загрузки комикса получен')

    params = add_required_params()    
    with open(f'comics{comics_extension}', 'rb') as photo:
        response = requests.post(upload_url, params=params, files={'photo': photo})
    response.raise_for_status()
    save_wall_upload_server_payload = response.json()
    print('Комикс загружен на сервер') 

    save_wall_photo_payload = post_request_vk_api(
        'photos.saveWallPhoto',
        {
            'server': save_wall_upload_server_payload['server'],
            'photo': save_wall_upload_server_payload['photo'],
            'hash': save_wall_upload_server_payload['hash'],
            'group_id': vk_group_id
        }
        ).json()
    print('Комикс сохранен в альбоме группы')   

    owner_id = save_wall_photo_payload["response"][0]["owner_id"]
    photo_id = save_wall_photo_payload["response"][0]["id"]
    wall_post_payload = post_request_vk_api(
        'wall.post',
        {
            'owner_id': f'-{vk_group_id}',
            'from_group': 1,
            'message': comics_text,
            'attachments': f'photo{owner_id}_{photo_id}'
        }
        )
    print('Комикс опубликован на стене группы')

    os.remove(f'comics{comics_extension}')
    print('Комикс удален из локальной директории')
    print('Скрипт завершил работу')
