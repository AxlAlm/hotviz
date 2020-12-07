from setuptools import setup
from hotviz import __version__, __author__, __author_email__, __license__

from setuptools import find_packages, setup

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

#PATH_ROOT = os.path.dirname(__file__)
builtins.__HOTVIZ_SETUP__ = True


setup(
    name='hotviz',
    version=__version__,    
    description='A visulizations lib for python',
    url='https://github.com/AxlAlm/hotviz',
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    packages=setuptools.find_packages(),
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
