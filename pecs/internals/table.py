from collections import MutableMapping, Sequence
import numpy as np


INDEX_SEPARATOR = '__to__'


class Table:

    def __init__(self, column_names, class_ids) -> None:
        self.__col_names = tuple(column_names)
        self.__row_length = len(column_names)
        self.__row_format = ''.join((" | {:>%s}" % (len(name)) for name in column_names))

        self._staged_adds = {}

        self.known_class_ids = tuple(class_ids)
        self.class_ids = []
        self.guids = []
        self.starts = []
        self.sizes = []

    @property
    def column_names(self):
        return self.__col_names

    def entity_class_from_tuple(self, sizes_tuple):
        assert len(sizes_tuple) == self.__row_length, "too many values"
        return tuple(0 if x == 0 else x / x for x in sizes_tuple)

    def stage_add(self, guid, value_tuple):
        assert guid not in self.guids, "guid must be unique"
        assert guid not in {t[0] for lst in self._staged_adds.values() for t in lst}, "cannot re-stage a staged guid"

        ent_class = self.entity_class_from_tuple(value_tuple)
        assert ent_class in self.known_class_ids, "added entity must correspond to a class id in the allocation schema"

        self._staged_adds.setdefault(ent_class, list()).append((guid, value_tuple))

    def stage_delete(self, guid):
        self.guids[self.guids.index(guid)] = None

    def make_starts_table(self):
        """Create a list of tuples where each value is the start index of that
        element. (Table is the sizes)
        """

    def section_slices(self):
        """Return a list of slices that represent the portions of each column
        that correspond to the known class ids in order. For known ids not
        present in class_ids, a zero-sized slice is used.
        """
        known_ids = self.known_class_ids
        id_column = self.class_ids

        expressed_ids = filter(lambda x : x in id_column, known_ids)
        starts = map(id_column.index, expressed_ids)
        # assert all(starts[x] < starts[x+1] for x in range(len(starts) - 1)), "id column must be in same order as known_ids"
        # stops = starts[1:] + [None]

    def guid_slices(self, guid):
        pass

    def rows_from_class_ids(self, class_ids):
        result = []
        starts = []
        return starts, result

    def mask_slices(self, col_names, indices):

        names = self.__col_names

        def to_indices(string, c_names = names, sep = INDEX_SEPARATOR):
            p1, p2 = string.split(sep)
            return c_names.index(p1), c_names.index(p2)

        mask_tuple = tuple(1 if n in col_names else 0 for n in names)

        def in_mask(item_tuple, mask=mask_tuple):
            return (x for x, m in zip(item_tuple, mask) if m)

        known_ids = self.known_class_ids
        matched_ids = {class_id for class_id in known_ids if all(in_mask(class_id))}
        starts, rows = self.rows_from_class_ids(matched_ids)

        for i, row in enumerate(rows):
            pass

    def compress(self):
        pass

    def slices_from_guid(self, guid):
        idx = self.guids.index(guid)
        starts = self.starts[idx]
        sizes = self.sizes[idx]
        return (slice(start, start + size, 1)
                for start, size in zip(starts, sizes))

    def show_sizes(self):
        pass

    def show_starts(self):
        pass

    def __str__(self):
        pass
