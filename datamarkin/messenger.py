import requests
import os
import magic
import json
import time
from .config import api_url, api_key
from tabulate import tabulate
import datamarkin.core


def check_resp(response):
    if response.status_code == 200:
        return response
    else:
        print("[INFO] API is not working. Status code :" + str(response.status_code))
        return None


def get_resp(url, headers=None, data=None, mode=1):
    if mode == 1:
        response = requests.get(url)

    elif mode == 2:
        response = requests.post(url, headers=headers, data=data)

    elif mode == 3:
        response = requests.patch(url, headers=headers, data=data)

    elif mode == 4:
        response = requests.delete(url, headers=headers, data=data)

    else:
        response = None

    return response


def waiting_response(url, headers=None, data=None, standby_time=1.0, mode=1):
    """ This function to delay requests """
    waiting_status_code_list = [404, 503]
    time.sleep(standby_time)
    response = get_resp(url, headers=headers, data=data, mode=mode)

    while response.status_code in waiting_status_code_list:
        if response.status_code == 404:
            standby_time += 5
            print("[INFO] API waiting. Status code : 404")
            time.sleep(standby_time)
            response = get_resp(url, headers=headers, data=data, mode=mode)
            if standby_time > 30:
                print("[INFO] Time out. Status code : 404")
                response = check_resp(response)
                break

        elif response.status_code == 503:
            standby_time = standby_time * (standby_time + 1)
            print("[INFO] API waiting. Status code : 503")
            time.sleep(standby_time)
            response = get_resp(url, headers=headers, data=data, mode=mode)

        else:
            response = check_resp(response)

    else:
        response = check_resp(response)

    return response


def get_item(url):
    response = requests.get(url)

    if response.status_code != 200:
        response = waiting_response(url, standby_time=0.1, mode=1)
        return response

    else:
        return response


def create_item(url, data):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        response = waiting_response(url, headers=headers, data=data, standby_time=0.1, mode=2)
        return response

    else:
        return response


def update_item(url, data):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    response = requests.patch(url, headers=headers, data=data)

    if response.status_code != 200:
        response = waiting_response(url, headers=headers, data=data, standby_time=0.1, mode=3)
        return response

    else:
        return response


def delete_item(url, data):
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    response = requests.delete(url, headers=headers, data=data)

    if response.status_code != 200:
        response = waiting_response(url, headers=headers, data=data, standby_time=1, mode=4)
        return response

    else:
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


def get_projects(items_per_request=-1, display=True):
    url = f"{api_url}/items/projects?sort=sort,-date_created&limit={items_per_request}&page=1&access_token={api_key}"
    response = get_item(url)
    info_projects = json.loads(response.content)
    num_projects = len(info_projects['data'])
    data = []
    col_names = ["Project Name", "Project ID", "Number of Class", "Project Type"]
    for i in range(num_projects):
        project_name = info_projects['data'][i]['name']
        project_id = info_projects['data'][i]['id']
        classes_info = info_projects['data'][i]['datasets']
        project_type = info_projects['data'][i]['type']
        data.append([project_name, project_id, len(classes_info), project_type])
    if display:
        print(tabulate(data, headers=col_names, tablefmt="pretty"))
    else:
        print('Number of Projects Found:::', num_projects)
        return info_projects


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


def new_get_projects(items_per_request=-1, sort="", search_filter=""):
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


def update_dataset():
    pass


def get_file_by_id(dataset_id, page=1):
    url = f"{api_url}/items/datasets_files?search={dataset_id}&limit={limit}&page={page}&access_token={api_key}"
    response = get_item(url)
    info_file = json.loads(response.content)
    return info_file


def get_project_datasets():
    print('datasets:')


def get_dataset_files():
    print('datasets:')


def download_file(file_id, file_dir):
    resp = get_file_request(file_id)
    get_write_file_with_requests(resp, file_dir, file_id)


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


def get_file_request(file_id, with_ext=False):
    file_url = "https://api.datamarkin.com/assets/" + file_id + "?access_token=" + api_key

    r = requests.get(file_url, stream=True)
    if r.status_code == 200:
        if with_ext:
            ext = r.headers['content-type'].split('/')[-1]
            return r, ext
        else:
            return r
    else:
        print("[INFO] API is not working. Status code :" + str(r.status_code))


def get_write_file_with_requests(r, file_dir, file_id, ext=None):
    if ext is not None:
        with open(file_dir + file_id + '.' + ext, 'wb') as f:
            f.write(r.content)
    else:
        with open(file_dir + file_id, 'wb') as f:
            f.write(r.content)


def get_list_of_items(collection, max_results=500, items_per_request=100, deep="", filter="filter", fields=""):
    list_of_items = []
    offset = 0
    max_iterate = int(max_results / items_per_request)

    for i in range(0, max_iterate):
        if collection == "files":
            url = f"{api_url}/{collection}?access_token={api_key}&limit={items_per_request}&offset={offset}&deep={deep}&{filter}&fields={fields}"
        else:
            url = f"{api_url}/items/{collection}?access_token={api_key}&limit={items_per_request}&offset={offset}&deep={deep}&{filter}&fields={fields}"

        response = get_item(url)
        response_content = json.loads(response.content)['data']
        if len(response_content) > 0:
            for item in response_content:
                list_of_items.append(item)
            offset = offset + items_per_request
            print("[INFO]", len(list_of_items), "images found and counting...")
        else:
            break
    return list_of_items
