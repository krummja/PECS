from collections import MutableMapping, Sequence
import numpy as np


class Table:

    def __init__(self, column_names, class_ids) -> None:
        self.__col_names = tuple(column_names)
        self.__row_length = len(column_names)
        self.__row_format = ''.join((" | {:>%s}" % (len(name)) for name in column_names))
        self._staged_adds = {}
        self.know_class_ids = tuple(class_ids)
        self.class_ids = []
        self.guids = []
        self.starts = []
        self.sizes = []

    @property
    def column_names(self):
        return self.__col_names

    def entity_class_from_tuple(self, sizes_tuple):
        pass

    def stage_add(self, guid, value_tuple):
        pass

    def stage_delete(self, guid):
        pass

    def make_starts_table(self):
        pass

    def section_slices(self):
        pass

    def guid_slices(self, guid):
        pass

    def rows_from_class_ids(self):
        pass

    def mask_slices(self, col_names, indices):
        pass

    def compress(self):
        pass

    def slices_from_guid(self, guid):
        pass

    def show_sizes(self):
        pass

    def show_starts(self):
        pass

    def __str__(self):
        pass
