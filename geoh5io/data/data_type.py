from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional, Type, cast

from geoh5io.shared import EntityType

from .color_map import ColorMap
from .geometric_data_constants import GeometricDataConstants
from .primitive_type_enum import PrimitiveTypeEnum

if TYPE_CHECKING:
    from geoh5io import workspace
    from . import data  # noqa: F401


class DataType(EntityType):
    def __init__(
        self,
        workspace: "workspace.Workspace",
        uid: uuid.UUID,
        primitive_type: PrimitiveTypeEnum,
    ):
        super().__init__(workspace, uid)
        self._primitive_type = primitive_type
        # TODO: define properties and setters
        self._color_map: Optional[ColorMap] = None
        self._units = None

    @staticmethod
    def _is_abstract() -> bool:
        return False

    @property
    def units(self) -> Optional[str]:
        return self._units

    @property
    def primitive_type(self) -> PrimitiveTypeEnum:
        return self._primitive_type

    @classmethod
    def create(
        cls, workspace: "workspace.Workspace", data_class: Type["data.Data"]
    ) -> DataType:
        """ Creates a new instance of DataType with the primitive type from the given Data
        implementation class.

        :param data_class: A Data implementation class.
        :return: A new instance of DataType.
        """
        uid = uuid.uuid4()
        primitive_type = data_class.primitive_type()
        return cls(workspace, uid, primitive_type)

    @classmethod
    def _for_geometric_data(
        cls, workspace: "workspace.Workspace", uid: uuid.UUID
    ) -> DataType:
        geom_primitive_type = GeometricDataConstants.primitive_type()
        data_type = cast(DataType, workspace.find_type(uid, DataType))
        if data_type is not None:
            assert data_type.primitive_type == geom_primitive_type
            return data_type
        return cls(workspace, uid, geom_primitive_type)

    @classmethod
    def for_x_data(cls, workspace: "workspace.Workspace") -> DataType:
        return cls._for_geometric_data(
            workspace, GeometricDataConstants.x_datatype_uid()
        )

    @classmethod
    def for_y_data(cls, workspace: "workspace.Workspace") -> DataType:
        return cls._for_geometric_data(
            workspace, GeometricDataConstants.y_datatype_uid()
        )

    @classmethod
    def for_z_data(cls, workspace: "workspace.Workspace") -> DataType:
        return cls._for_geometric_data(
            workspace, GeometricDataConstants.z_datatype_uid()
        )