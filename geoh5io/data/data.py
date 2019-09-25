import uuid
from abc import abstractmethod

from .data_association_enum import DataAssociationEnum
from .data_type import DataType
from .primitive_type_enum import PrimitiveTypeEnum
from geoh5io.shared import Entity


class Data(Entity):
    def __init__(
        self,
        data_type: DataType,
        association: DataAssociationEnum,
        name: str,
        uid: uuid.UUID = None,
    ):
        super().__init__(name, uid)
        self._association = association
        self._type = data_type

    @property
    def association(self) -> DataAssociationEnum:
        return self._association

    def get_type(self) -> DataType:
        return self._type

    @classmethod
    @abstractmethod
    def primitive_type(cls) -> PrimitiveTypeEnum:
        ...
