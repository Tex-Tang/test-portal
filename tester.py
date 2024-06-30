# Abstract class

import abc
from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo
from typing import List, Type


def create_list_model(model: Type[BaseModel]) -> Type[BaseModel]:
    fields = model.model_fields
    annotations = {name: List[field.annotation] for name, field in fields.items()}
    return type(f"{model.__name__}List", (BaseModel,), {"__annotations__": annotations})


class Tester(abc.ABC):
    def run(self, parameter):
        raise NotImplementedError

    @classmethod
    def get_config_model(self):
        raise NotImplementedError

    @classmethod
    def get_parameter_model(self):
        raise NotImplementedError

    @classmethod
    def get_parameter_lists(self):
        parameter_model = self.get_parameter_model()
        return create_list_model(parameter_model)
