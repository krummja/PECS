from __future__ import annotations
from beartype.typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pecs_framework.component import Component

import os
from importlib import import_module


class Loader:

    def __init__(self, file: str) -> None:
        here = os.path.dirname(os.path.abspath(file))
        self.tree = os.listdir(here)
        self.tree.remove("__init__.py")
        self.tree.remove("__pycache__")
        
        self._components = []

    @property
    def components(self) -> list[type[Component]]:
        return self._components

    def load(self, pathspec: str) -> None:
        for file in self.tree:
            file_name = file.replace(".py", "")
            module_name = file_name.replace("_", "")

            module = import_module("." + module_name, pathspec)
            for key in vars(module).keys():
                if key.lower() == module_name:
                    self._components.append(vars(module)[key])
