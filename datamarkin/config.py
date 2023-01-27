"""
 The default configuration contains the parameters used for troubleshooting in case of
mismatch with the minimum parameter keys.

### Key Descriptions

*Usage of parameters varies by application type

tl: Transfer learning mode selection(only object detection) / type: int
step_size: Parameter for learning rate finder               / type: int
val_split: Validation split size                            / type: float, 0 to 1
test_split: Test split size                                 / type: float, 0 to 1
batch_size: Batch size                                      / type: int
num_epochs: Train epoch number                              / type: int
model_display: Print model architecture                     / type: int , 0 or 1
img_size: None, default and custom size                     / type: list, [w, h, d]
augment_factor: Augment function definition                 / type: dict
"""

api_key = 'YOUR_API_KEY'
api_url = 'https://api.datamarkin.com'

default_img_size = {
    'tf-mobilenetv2': [224, 224, 3],
    'tf-mobilenetv3': [224, 224, 3],
    'tf-efficientnetb0': [224, 224, 3],
    'tf-efficientnetb1': [240, 240, 3],
    'tf-efficientnetb2': [260, 260, 3],
    'tf-efficientnetb3': [300, 300, 3],
    'tf-efficientnetb4': [380, 380, 3],
    'tf-efficientnetb5': [456, 456, 3],
    'tf-efficientnetb6': [528, 528, 3],
    'tf-efficientnetb7': [600, 600, 3]
}

# SETTINGS
default_config = {
    "image-classification":
    {
        "train": {
            "step_size": 8,
            "val_split": 0.1,
            "batch_size": 48,
            "num_epochs": 50,
            "test_split": 0.1,
            "img_size": default_img_size,
            "augment_settings": {
                    "step1": {
                        "transform": {
                            "p": 1,
                            "transforms": [
                                {
                                    "p": 1,
                                    "transforms": [
                                        {
                                            "p": 0.5,
                                            "transforms": [
                                                {
                                                    "p": 0.5,
                                                    "always_apply": False,
                                                    "__class_fullname__": "HorizontalFlip"
                                                },
                                                {
                                                    "p": 1,
                                                    "value": None,
                                                    "mask_value": None,
                                                    "border_mode": 1,
                                                    "scale_limit": [
                                                        -0.09999999999999998,
                                                        0.10000000000000007
                                                    ],
                                                    "always_apply": False,
                                                    "rotate_limit": [
                                                        -45,
                                                        45
                                                    ],
                                                    "interpolation": 1,
                                                    "shift_limit_x": [
                                                        -0.0625,
                                                        0.0625
                                                    ],
                                                    "shift_limit_y": [
                                                        -0.0625,
                                                        0.0625
                                                    ],
                                                    "__class_fullname__": "ShiftScaleRotate"
                                                }
                                            ],
                                            "__class_fullname__": "Sequential"
                                        },
                                        {
                                            "p": 0.5,
                                            "transforms": [
                                                {
                                                    "p": 0.5,
                                                    "always_apply": False,
                                                    "__class_fullname__": "VerticalFlip"
                                                },
                                                {
                                                    "p": 1,
                                                    "always_apply": False,
                                                    "contrast_limit": [
                                                        -0.2,
                                                        0.2
                                                    ],
                                                    "brightness_limit": [
                                                        -0.2,
                                                        0.2
                                                    ],
                                                    "brightness_by_max": True,
                                                    "__class_fullname__": "RandomBrightnessContrast"
                                                }
                                            ],
                                            "__class_fullname__": "Sequential"
                                        }
                                    ],
                                    "__class_fullname__": "OneOf"
                                }
                            ],
                            "bbox_params": None,
                            "keypoint_params": None,
                            "__class_fullname__": "Compose",
                            "additional_targets": {}
                        }
                    },
                    "step2": 'default'
                            }
        }
    },
    "multilabel-image-classification": {
        "train": {
            "step_size": 8,
            "val_split": 0.1,
            "batch_size": 48,
            "num_epochs": 50,
            "test_split": 0.1,
            "img_size": default_img_size
        }
    },
    "object-detection":
        {
            "train": {
                "tl": 1,
                "step_size": 8,
                "val_split": 0.1,
                "batch_size": 2,
                "num_epochs": 50,
                "test_split": 0.1,
                "model_display": 0
            }
        },
    "keypoint-detection":
        {
            "train": {

            }
        },
    "image-segmentation":
        {
            "train": {

            }
        }
    }