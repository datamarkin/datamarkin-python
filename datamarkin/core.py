import time
import numpy
import json
from multiprocessing.pool import ThreadPool as Pool



def upload_file_to_dataset(file, dataset_id, url, labels=None):
    data = {"annotations": labels}
    upload_result = API.messenger.upload_file(file, payload=data)
    directus_files_id = upload_result['data']['id']

    if upload_result.__contains__('data'):
        data = {
            "datasets_id": dataset_id,
            "directus_files_id": directus_files_id
        }
        data = json.dumps(data)
        API.messenger.create_item(url, data)
    else:
        print('error')


class Project:
    def __init__(self, project_id, status, user_created, date_created, user_updated, date_updated, name, project_type,
                 train, model_architecture, description, datasets, configuration, trainings, augmentation):
        self.id = project_id
        self.status = status
        self.user_created = API.messenger.get_user_by_id(user_created)
        self.date_created = date_created
        self.user_updated = API.messenger.get_user_by_id(user_updated)
        self.date_updated = date_updated
        self.name = name
        self.type = project_type
        self.train = train
        self.model_architecture = model_architecture
        self.description = description
        self.datasets = Dataset.create_dataset_list(datasets)
        self.configuration = configuration
        self.trainings = Training.create_training_list(trainings)
        self.augmentation = augmentation

    def update_project(self):
        data = {
            "status": self.status,
            "train": self.train,
            "description": self.description
        }
        data = json.dumps(data)
        response = API.messenger.new_update_project(self.id, data)
        return response

    def health(self):
        dataset_health = self.check_dataset_health()
        return dataset_health

    def check_dataset_health(self):
        if self.type == 'image-classification':
            for dataset in self.datasets:
                if len(dataset.images) < 10:
                    dataset_len = False
                    break
                else:
                    dataset_len = True

            if len(self.datasets) < 2:
                return False
            elif not dataset_len:
                return False
            else:
                return True
        else:
            return True

    def pre_inspection(self):
        self.check_configuration()
        self.check_augmentation()
        return True

    def check_configuration(self):
        if self.configuration is None:
            self.configuration = {
                "train": {"step_size": 8, "val_split": 0.1, "batch_size": 2, "num_epochs": 75, "test_split": 0.1}}
            self.update_project()
        return True

    def check_augmentation(self):
        if self.augmentation is None:
            self.augmentation = {"step1": "default"}
            self.update_project()
        self.check_configuration_health()
        self.update_project()
        return True

    def check_configuration_health(self):
        """ Configuration keys are checked to avoid potential problems. """
        if self.configuration is None:
            self.configuration = default_config[self.type]
            self.configuration["train"]["img_size"] = default_config[self.type]["train"]["img_size"][self.model_architecture]
        else:
            for key in list(default_config[self.type]["train"].keys()):
                if key in list(self.configuration["train"].keys()):
                    if key == "img_size" and self.configuration["train"][key] is None:
                        self.configuration["train"][key] = default_config[self.type]["train"][key][self.model_architecture]
                    elif self.configuration["train"][key] is None:
                        self.configuration["train"][key] = default_config[self.type]["train"][key]
                    else:
                        pass
                else:
                    if key == "img_size":
                        self.configuration["train"][key] = default_config[self.type]["train"][key][self.model_architecture]
                    else:
                        self.configuration["train"][key] = default_config[self.type]["train"][key]


class User:
    def __init__(self, user_id, first_name, last_name, email, location, title, description, tags, language, tfa_secret,
                 status, role, token, last_access, plan_id):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.location = location
        self.title = title
        self.description = description
        self.tags = tags
        self.language = language
        self.tfa_secret = tfa_secret
        self.status = status
        self.role = role
        self.token = token
        self.last_access = last_access
        self.plan = API.messenger.get_plan_by_id(plan_id)


class Dataset:
    def __init__(self, dataset_id, status, user_created, date_created, user_updated, date_updated, name, project,
                 images):
        self.id = dataset_id
        self.status = status
        self.user_created_id = user_created
        self.date_created = date_created
        self.user_updated_id = user_updated
        self.date_updated = date_updated
        self.name = name if name != '' else dataset_id
        self.project = project
        self.images = images

    def upload_files_to_dataset(self, match_dict):
        url = "https://api.datamarkin.com/items/datasets_files?access_token"

        files, labels = match_dict[self.name]['files'], match_dict[self.name]['labels']

        pool = Pool(processes=3)
        if labels is []:
            for file in files:
                pool.apply_async(upload_file_to_dataset, (file, self.id, url,))
        else:
            for idx in range(len(files)):
                pool.apply_async(upload_file_to_dataset, (files[idx], self.id, url, labels[idx],))

        pool.close()
        start = time.time()
        pool.join()
        print("[INFO] Dataset", self.name, "uploaded in:", round(time.time() - start), "secs")

    @staticmethod
    def create_dataset_list(datasets):
        dataset_list = []
        for dataset in datasets:
            dataset = API.messenger.get_dataset_by_id(dataset)
            dataset_list.append(dataset)
        return dataset_list


class Training:
    def __init__(self, training_id, status, user_created, date_created, user_updated, date_updated, lr_min, lr_max,
                 project, model_architecture, duration, configuration):
        self.id = training_id
        self.status = status
        self.user_created_id = user_created
        self.date_created = date_created
        self.user_updated_id = user_updated
        self.date_updated = date_updated
        self.lr_min = lr_min
        self.lr_max = lr_max
        self.confusion_matrix = None
        self.lrfind_plot = None
        self.lr_plot = None
        self.history = None
        self.project_id = project
        self.model_architecture = model_architecture
        self.duration = duration
        self.model_tensorflow = None
        self.model_coreml = None
        self.model_onnx = None
        self.model_keras = None
        self.model_tensorflowjs = None
        self.model_tensorflowlite = None
        self.model_pytorch = None
        self.log = None
        self.configuration = configuration
        self.vision_servers = None

    def update_training(self):
        data = {
            "status": self.status,
            "lr_min": self.lr_min,
            "lr_max": self.lr_max,
            "duration": self.duration,
            "model_architecture": self.model_architecture,
            "confusion_matrix": self.confusion_matrix,
            "lrfind_plot": self.lrfind_plot,
            "lr_plot": self.lr_plot,
            "history": self.history,
            "model_tensorflow": self.model_tensorflow,
            "model_coreml": self.model_coreml,
            "model_onnx": self.model_onnx,
            "model_keras": self.model_keras,
            "model_tensorflowjs": self.model_tensorflowjs,
            "model_tensorflowlite": self.model_tensorflowlite,
            "model_pytorch": self.model_pytorch,
            "log": self.log,
            "configuration": self.configuration,
            "vision_servers": self.vision_servers
        }
        data = json.dumps(data, cls=NumpyEncoder)
        response = API.messenger.update_training(self.id, data)
        return response

    @staticmethod
    def create_training_list(trainings):
        training_list = []
        for training in trainings:
            training = API.messenger.get_training_by_id(training)
            training_list.append(training)
        return training_list


class Plan:
    def __init__(self, plan_id, status, price, limits, name, code, description):
        self.id = plan_id
        self.status = status
        self.price = price
        self.limits = limits
        self.name = name
        self.code = code
        self.description = description


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)
