
#metadata
__version__ = "0.0.6"
__author__ =  "Axel Almquist"
__author_email__ =  "axel@almquist.io"
__license__ = "MIT"

try:
    __HOTVIZ_SETUP__
except NameError:
    __HOTVIZ_SETUP__ = False


if not __HOTVIZ_SETUP__:

    from hotviz.hot_text import hot_text
    from hotviz.hot_tree import hot_tree

    __all__ = [
                "hot_text",
                "hot_tree"
                ]