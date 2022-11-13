from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    pass

import timeit
import attic.numpy_tests as pecs


class ContactData(pecs.Component):

    def __init__(self, first_name, last_name) -> None:
        self.first_name = first_name
        self.last_name = last_name


class CompanyData(pecs.Component):

    def __init__(self, cdomain, company_name) -> None:
        self.cdomain = cdomain
        self.company_name = company_name


class TestBase:

    ecs: pecs.Engine
    world: pecs.World

    def __init__(self):
        self.ecs = pecs.Engine()
        self.ecs.register_component(ContactData)
        self.ecs.register_component(CompanyData)
        self.world = self.ecs.create_world()
        self.prefabs = {}
