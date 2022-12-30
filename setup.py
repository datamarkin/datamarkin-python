from setuptools import setup

setup(
    name='datamarkin',
    version='1.0.7.dev1',
    description='Datamarkin python client',
    url='https://github.com/datamarkin/datamarkin-python',
    author='Datamarkin',
    author_email='support@datamarkin.com',
    license='Apache-2.0 license',
    packages=['datamarkin'],
    python_requires='>=3',
    install_requires=[
                      'requests'
                      ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
)