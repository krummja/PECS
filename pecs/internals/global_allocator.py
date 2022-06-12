
def verify_component_schema(allocation_schema):
    pass


class GlobalAllocator:

    def __init__(self, components, allocation_scheme):
        pass

    def accessor_from_guid(self):
        pass

    @property
    def next_guid(self):
        return

    @property
    def guids(self):
        return

    def add(self, values_dict, guid=None):
        pass

    def delete(self, guid):
        pass

    def _defragment(self):
        pass

    def is_valid_query(self):
        pass

    def selectors_from_component_query(self, query, sep):
        pass
