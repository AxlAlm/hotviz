from setuptools import find_packages, setup

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

builtins.__HOTVIZ_SETUP__ = True

import hotviz


setup(
    name='hotviz',
    version=hotviz.__version__,    
    description='A visulizations lib for python',
    url='https://github.com/AxlAlm/hotviz',
    author=hotviz.__author__,
    author_email=hotviz.__author_email__,
    license=hotviz.__license__,
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
