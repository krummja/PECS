import sys
import numpy as np


class Accessor:

    def __init__(self, guid):
        pass

    def _rebuild_references(self, build_ref):
        pass

    def __repr__(self):
        pass


class AccessorFactory:

    def __init__(self, allocator):
        self.allocator = allocator

    def attribute_getter_factory(self, component_name):
        pass

    def attribute_setter_factory(self, component_name):
        pass

    def generate_accessor(self):
        pass
