from __future__ import annotations
from beartype import beartype
from beartype.typing import *
from beartype.vale import Is
from typing import Annotated, TypeAlias


HasComponentID = Is[lambda cls: hasattr(cls, '__component_id__')]
Component_ = Annotated[type, HasComponentID]
IdStr = Annotated[str, Is[lambda id_str: id_str == id_str.upper()]]

Bases: TypeAlias = tuple[type, ...]
Namespace: TypeAlias = dict[str, Any]


class ComponentMeta(type):
    """Base Component Metaclass"""
    comp_id: str
    cbits: int
    
    def __new__(
            mcs: Type[ComponentMeta], 
            clsname: str, 
            bases: Bases, 
            namespace: Namespace,
        ) -> ComponentMeta:
        clsobj = super().__new__(mcs, clsname, bases, namespace)
        clsobj.comp_id = clsname.upper()
        clsobj.cbits = 1
        return clsobj
    
    
class Component(metaclass=ComponentMeta):
   """Root Component class that all components extend."""
   
   @property
   def classtype(self) -> ComponentMeta:
       return self.__class__
