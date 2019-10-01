import uuid

from .object_base import ObjectBase, ObjectType


class Drillhole(ObjectBase):
    __TYPE_UID = uuid.UUID(
        fields=(0x7CAEBF0E, 0xD16E, 0x11E3, 0xBC, 0x69, 0xE4632694AA37)
    )

    def __init__(self, object_type: ObjectType, name: str, uid: uuid.UUID = None):
        super().__init__(object_type, name, uid)
        # TODO
        # self._vertices = []
        # self._cells = []
        # self._collar = None
        # self._surveys = []
        # self._trace = []

    @classmethod
    def default_type_uid(cls) -> uuid.UUID:
        return cls.__TYPE_UID