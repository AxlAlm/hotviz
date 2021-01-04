from setuptools import find_packages, setup
import json
import pathlib
import os


def get_meta():
    meta_file = os.path.join(pathlib.Path(__file__).parent.absolute(), "meta.json")
    with open(meta_file, "r") as f:
        meta = json.load(f)
    return meta

meta = get_meta()


setup(
    name='hotviz',
    version=meta["__version__"],    
    description='A visulizations lib for python',
    url='https://github.com/AxlAlm/hotviz',
    author=meta["__author__"],
    author_email=meta["__author_email__"],
    license=meta["__license__"],
    packages=find_packages(),
    install_requires=[
                        'numpy==1.18.1',
                        'plotly==4.9.0',
                        'python-igraph==0.8.3',
                        'imgkit==1.0.2',                  
                      ],

    classifiers=[
                'Development Status :: 4 - Beta',
                'Programming Language :: Python :: 3.7',
                ],
)
