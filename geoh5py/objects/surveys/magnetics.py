#  Copyright (c) 2021 Mira Geoscience Ltd.
#
#  This file is part of geoh5py.
#
#  geoh5py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  geoh5py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with geoh5py.  If not, see <https://www.gnu.org/licenses/>.

import uuid

from ..curve import Curve
from ..object_type import ObjectType


class AirborneMagnetics(Curve):
    """
    An airborne magnetic survey object.

    .. warning:: Partially implemented.

    """

    __TYPE_UID = uuid.UUID(
        fields=(0x4B99204C, 0xD133, 0x4579, 0xA9, 0x16, 0xA9C8B98CFCCB)
    )

    def __init__(self, object_type: ObjectType, **kwargs):
        super().__init__(object_type, **kwargs)

    @classmethod
    def default_type_uid(cls) -> uuid.UUID:
        """
        :return: Default unique identifier
        """
        return cls.__TYPE_UID
