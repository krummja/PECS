from __future__ import annotations
from beartype.typing import *

if TYPE_CHECKING:
    from pecs_framework.entity import Entity

from pecs_framework._types import Bases, Namespace


class ComponentMeta(type):
    """Base Component Metaclass"""
    comp_id: str
    cbits: int
    entity: Entity
    
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
