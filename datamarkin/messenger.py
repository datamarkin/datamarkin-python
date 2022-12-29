import requests
import os
import magic
import json
from .config import api_url, api_key


def get_item(url):
    response = requests.get(url)
    return response


def create_item(url, data):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    response = requests.post(url, headers=headers, data=data)

    return response


def update_item(url, data):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    response = requests.patch(url, headers=headers, data=data)

    return response


def delete_item(url, data):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    response = requests.delete(url, headers=headers, data=data)

    return response


def upload_files(path_list):
    files = {}
    url = f"{api_url}/files?access_token={api_key}"

    for image in path_list:
        filename = os.path.basename(image)
        mime = magic.Magic(mime=True)
        files[filename] = (filename, open(image, 'rb'), mime.from_file(image), {'Expires': '0'})

    response = requests.post(url, files=files)
    info_files = json.loads(response.content)
    return info_files


def upload_file(path):
    url = f"{api_url}/files?access_token={api_key}"

    filename = os.path.basename(path)
    mime = magic.Magic(mime=True)
    file = {filename: (filename, open(path, 'rb'), mime.from_file(path), {'Expires': '0'})}

    response = requests.post(url, files=file)
    info_file = json.loads(response.content)
    return info_file


def get_projects(items_per_request=-1, sort="", search_filter=""):
    url = f"{api_url}/items/projects?sort={sort}&limit={items_per_request}&page=1&filter{search_filter}&access_token={api_key}"
    response = get_item(url)

    if response is None:
        return []

    info_projects = json.loads(response.content)
    project_list = []

    for project in info_projects['data']:
        x = datamarkin.core.Project(project['id'],
                                    project['status'],
                                    project['user_created'],
                                    project['date_created'],
                                    project['user_updated'],
                                    project['date_updated'],
                                    project['name'],
                                    project['type'],
                                    project['train'],
                                    project['model_architecture'],
                                    project['description'],
                                    project['datasets'],
                                    project['configuration'],
                                    project['trainings'],
                                    project['augmentation'])
        project_list.append(x)
    return project_list


def get_project_by_id(project_id, deep={"datasets": {"_limit": 750}}):
    deep = json.dumps(deep)
    url = f"{api_url}/items/projects/{project_id}?access_token={api_key}&deep={deep}"
    response = get_item(url)
    info_project = json.loads(response.content)
    project = datamarkin.core.Project(info_project['data']['id'],
                                      info_project['data']['status'],
                                      info_project['data']['user_created'],
                                      info_project['data']['date_created'],
                                      info_project['data']['user_updated'],
                                      info_project['data']['date_updated'],
                                      info_project['data']['name'],
                                      info_project['data']['type'],
                                      info_project['data']['train'],
                                      info_project['data']['model_architecture'],
                                      info_project['data']['description'],
                                      info_project['data']['datasets'],
                                      info_project['data']['configuration'],
                                      info_project['data']['trainings'],
                                      info_project['data']['augmentation'])
    project.pre_inspection()
    return project


def get_dataset_by_id(dataset_id):
    url = f"{api_url}/items/datasets/{dataset_id}?access_token={api_key}"
    response = get_item(url)
    info_dataset = json.loads(response.content)['data']

    dataset = datamarkin.core.Dataset(info_dataset['id'],
                                      info_dataset['status'],
                                      info_dataset['user_created'],
                                      info_dataset['date_created'],
                                      info_dataset['user_updated'],
                                      info_dataset['date_updated'],
                                      info_dataset['name'],
                                      info_dataset['project'],
                                      info_dataset['images'])
    return dataset


def get_file_by_id(dataset_id, page=1):
    limit = -1
    url = f"{api_url}/items/datasets_files?search={dataset_id}&limit={limit}&page={page}&access_token={api_key}"
    response = get_item(url)
    info_file = json.loads(response.content)
    return info_file


def create_project(data):
    url = f"{api_url}/items/projects/?access_token={api_key}"
    print(data)
    response = create_item(url, data)
    response = json.loads(response.content)
    project_id = response['data']['id']
    project = get_project_by_id(project_id)
    return project


def update_project(project_id, data):
    url = f"{api_url}/items/projects/{project_id}?access_token={api_key}"
    data = data
    response = update_item(url, data)
    info_project = json.loads(response.content)
    return info_project


def get_user_by_id(user_id):
    if user_id:
        url = f"{api_url}/users/{user_id}?access_token={api_key}"
        response = get_item(url)
        info_user = json.loads(response.content)
        user = datamarkin.core.User(info_user['data']['id'],
                                    info_user['data']['first_name'],
                                    info_user['data']['last_name'],
                                    info_user['data']['email'],
                                    info_user['data']['location'],
                                    info_user['data']['title'],
                                    info_user['data']['description'],
                                    info_user['data']['tags'],
                                    info_user['data']['language'],
                                    info_user['data']['tfa_secret'],
                                    info_user['data']['status'],
                                    info_user['data']['role'],
                                    info_user['data']['token'],
                                    info_user['data']['last_access'],
                                    info_user['data']['plan'])
        return user
    else:
        return None


def get_plan_by_id(plan_id):
    if plan_id:
        url = f"{api_url}/items/plans/{plan_id}?access_token={api_key}"
        response = get_item(url)
        info_plan = json.loads(response.content)['data']
        plan = datamarkin.core.Plan(info_plan['id'],
                                    info_plan['status'],
                                    info_plan['price'],
                                    info_plan['limits'],
                                    info_plan['name'],
                                    info_plan['code'],
                                    info_plan['description'])
        return plan
    else:
        return None


def new_update_project(project_id, data):
    url = f"{api_url}/items/projects/{project_id}?access_token={api_key}"
    response = update_item(url, data)
    info_project = json.loads(response.content)

    return info_project


def get_training_by_id(training_id):
    if training_id:
        url = f"{api_url}/items/trainings/{training_id}?access_token={api_key}"
        response = get_item(url)
        info_training = json.loads(response.content)['data']
        training = datamarkin.core.Training(info_training['id'],
                                            info_training['status'],
                                            info_training['user_created'],
                                            info_training['date_created'],
                                            info_training['user_updated'],
                                            info_training['date_updated'],
                                            info_training['lr_min'],
                                            info_training['lr_max'],
                                            info_training['project'],
                                            info_training['model_architecture'],
                                            info_training['duration'],
                                            info_training['configuration'])
        return training
    else:
        return None


def create_training(project):
    url = f"{api_url}/items/trainings/?access_token={api_key}"
    data = '{{"project":"{0}"}}'.format(project.id)
    response = create_item(url, data)
    info_training = json.loads(response.content)['data']
    info_training['user_created'] = project.user_created.id
    info_training['model_architecture'] = project.model_architecture
    info_training['configuration'] = project.configuration
    info_training['configuration']['train']['augment_settings'] = project.augmentation
    info_training['status'] = "draft"

    training = datamarkin.core.Training(info_training['id'],
                                        info_training['status'],
                                        info_training['user_created'],
                                        info_training['date_created'],
                                        info_training['user_updated'],
                                        info_training['date_updated'],
                                        info_training['lr_min'],
                                        info_training['lr_max'],
                                        info_training['project'],
                                        info_training['model_architecture'],
                                        info_training['duration'],
                                        info_training['configuration'])
    return training


def update_training(training_id, data):
    url = f"{api_url}/items/trainings/{training_id}?access_token={api_key}"
    data = data
    response = update_item(url, data)
    info_training = json.loads(response.content)
    return info_training
