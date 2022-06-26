import numpy as np


class DefraggingArrayComponent:

    def __init__(self, name, dim, dtype, size=0):
        pass

    def assert_capacity(self, new_capacity):
        pass

    def reallocate(self, old_selector, new_selector):
        pass

    def __getitem__(self, selector):
        pass

    def __setitem__(self, selector, data):
        pass

    def _resize_multidim(self, count):
        pass

    def _resize_singledim(self, count):
        pass

    def __repr__(self):
        pass
