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

# pylint: disable=R0902

from __future__ import annotations

import uuid

import numpy as np

from ..data.data import Data
from ..shared.utils import match_values, merge_arrays
from .object_base import ObjectType
from .points import Points


class Drillhole(Points):
    """
    Drillhole object class defined by

    .. warning:: Not yet implemented.

    """

    __TYPE_UID = uuid.UUID(
        fields=(0x7CAEBF0E, 0xD16E, 0x11E3, 0xBC, 0x69, 0xE4632694AA37)
    )
    _attribute_map = Points._attribute_map.copy()
    _attribute_map.update(
        {
            "Cost": "cost",
            "Collar": "collar",
            "Planning": "planning",
        }
    )

    def __init__(self, object_type: ObjectType, **kwargs):
        self._cells: np.ndarray | None = None
        self._collar: np.ndarray | None = None
        self._cost: float | None = 0.0
        self._planning: str = "Default"
        self._surveys: np.ndarray = None
        self._trace: np.ndarray = None
        self._trace_depth: np.ndarray | None = None
        self._locations = None
        self._deviation_x = None
        self._deviation_y = None
        self._deviation_z = None
        self._default_collocation_distance = 1e-2

        super().__init__(object_type, **kwargs)

    @classmethod
    def default_type_uid(cls) -> uuid.UUID:
        return cls.__TYPE_UID

    @property
    def cells(self) -> np.ndarray | None:
        r"""
        :obj:`numpy.ndarray` of :obj:`int`, shape (\*, 2):
        Array of indices defining segments connecting vertices.
        """
        if getattr(self, "_cells", None) is None:
            if self.existing_h5_entity:
                self._cells = self.workspace.fetch_cells(self.uid)

        return self._cells

    @cells.setter
    def cells(self, indices):
        assert indices.dtype == "uint32", "Indices array must be of type 'uint32'"
        self.modified_attributes = "cells"
        self._cells = indices

    @property
    def collar(self):
        """
        :obj:`numpy.array` of :obj:`float`, shape (3, ): Coordinates of the collar
        """
        return self._collar

    @collar.setter
    def collar(self, value):
        if value is not None:
            if isinstance(value, np.ndarray):
                value = value.tolist()

            assert len(value) == 3, "Origin must be a list or numpy array of shape (3,)"

            self.modified_attributes = "attributes"
            value = np.asarray(
                tuple(value), dtype=[("x", float), ("y", float), ("z", float)]
            )
            self._collar = value
        self._locations = None

        if self.trace is not None:
            self.modified_attributes = "trace"
            self._trace = None

    @property
    def cost(self):
        """
        :obj:`float`: Cost estimate of the drillhole
        """
        return self._cost

    @cost.setter
    def cost(self, value):
        assert isinstance(value, float), f"Provided cost value must be of type {float}"
        self._cost = value

    @property
    def deviation_x(self):
        """
        :obj:`numpy.ndarray`: Store the change in x-coordinates along the well path.
        """
        if getattr(self, "_deviation_x", None) is None and self.surveys is not None:
            lengths = self.surveys[1:, 0] - self.surveys[:-1, 0]
            dl_in = np.cos(np.deg2rad(450.0 - self.surveys[:-1, 2] % 360.0)) * np.cos(
                np.deg2rad(self.surveys[:-1, 1])
            )
            dl_out = np.cos(np.deg2rad(450.0 - self.surveys[1:, 2] % 360.0)) * np.cos(
                np.deg2rad(self.surveys[1:, 1])
            )
            ddl = np.divide(dl_out - dl_in, lengths, where=lengths != 0)
            self._deviation_x = dl_in + lengths * ddl / 2.0

        return self._deviation_x

    @property
    def deviation_y(self):
        """
        :obj:`numpy.ndarray`: Store the change in y-coordinates along the well path.
        """
        if getattr(self, "_deviation_y", None) is None and self.surveys is not None:
            lengths = self.surveys[1:, 0] - self.surveys[:-1, 0]
            dl_in = np.sin(np.deg2rad(450.0 - self.surveys[:-1, 2] % 360.0)) * np.cos(
                np.deg2rad(self.surveys[:-1, 1])
            )
            dl_out = np.sin(np.deg2rad(450.0 - self.surveys[1:, 2] % 360.0)) * np.cos(
                np.deg2rad(self.surveys[1:, 1])
            )
            ddl = np.divide(dl_out - dl_in, lengths, where=lengths != 0)
            self._deviation_y = dl_in + lengths * ddl / 2.0

        return self._deviation_y

    @property
    def deviation_z(self):
        """
        :obj:`numpy.ndarray`: Store the change in z-coordinates along the well path.
        """
        if getattr(self, "_deviation_z", None) is None and self.surveys is not None:
            lengths = self.surveys[1:, 0] - self.surveys[:-1, 0]
            dl_in = np.sin(np.deg2rad(self.surveys[:-1, 1]))
            dl_out = np.sin(np.deg2rad(self.surveys[1:, 1]))
            ddl = np.divide(dl_out - dl_in, lengths, where=lengths != 0)
            self._deviation_z = dl_in + lengths * ddl / 2.0

        return self._deviation_z

    @property
    def locations(self):
        """
        :obj:`numpy.ndarray`: Lookup array of the well path x,y,z coordinates.
        """
        if (
            getattr(self, "_locations", None) is None
            and self.collar is not None
            and self.surveys is not None
        ):
            lengths = self.surveys[1:, 0] - self.surveys[:-1, 0]
            self._locations = np.c_[
                self.collar["x"] + np.cumsum(np.r_[0.0, lengths * self.deviation_x]),
                self.collar["y"] + np.cumsum(np.r_[0.0, lengths * self.deviation_y]),
                self.collar["z"] + np.cumsum(np.r_[0.0, lengths * self.deviation_z]),
            ]

        return self._locations

    @property
    def planning(self):
        """
        :obj:`str`: Status of the hole: ["Default", "Ongoing", "Planned", "Completed"]
        """
        return self._planning

    @planning.setter
    def planning(self, value):
        choices = ["Default", "Ongoing", "Planned", "Completed"]
        assert value in choices, f"Provided planning value must be one of {choices}"
        self._planning = value

    @property
    def surveys(self):
        """
        :obj:`numpy.array` of :obj:`float`, shape (3, ): Coordinates of the surveys
        """
        if (getattr(self, "_surveys", None) is None) and self.existing_h5_entity:
            self._surveys = self.workspace.fetch_coordinates(self.uid, "surveys")

        if getattr(self, "_surveys", None) is not None:
            surveys = self._surveys.view("<f4").reshape((-1, 3))

            # Repeat first survey point at surface for de-survey interpolation
            surveys = np.vstack([surveys[0, :], surveys])
            surveys[0, 0] = 0.0

            return surveys.astype(float)

        return None

    @surveys.setter
    def surveys(self, value):
        if value is not None:
            value = np.vstack(value)

            if value.shape[1] != 3:
                raise ValueError("'surveys' requires an ndarray of shape (*, 3)")

            self.modified_attributes = "surveys"
            self._surveys = np.asarray(
                np.core.records.fromarrays(
                    value.T, names="Depth, Dip, Azimuth", formats="<f4, <f4, <f4"
                )
            )
            self.modified_attributes = "trace"
            self._trace = None
        self._deviation_x = None
        self._deviation_y = None
        self._deviation_z = None
        self._locations = None

    @property
    def default_collocation_distance(self):
        """
        Minimum collocation distance for matching depth on merge
        """
        return self._default_collocation_distance

    @default_collocation_distance.setter
    def default_collocation_distance(self, tol):
        assert tol > 0, "Tolerance value should be >0"
        self._default_collocation_distance = tol

    @property
    def trace(self) -> np.ndarray | None:
        """
        :obj:`numpy.array`: Drillhole trace defining the path in 3D
        """
        if (getattr(self, "_trace", None) is None) and self.existing_h5_entity:
            self._trace = self.workspace.fetch_coordinates(self.uid, "trace")

        if getattr(self, "_trace", None) is not None:
            return self._trace.view("<f8").reshape((-1, 3))

        return None

    @property
    def trace_depth(self) -> np.ndarray | None:
        """
        :obj:`numpy.array`: Drillhole trace depth from top to bottom
        """
        if getattr(self, "_trace_depth", None) is None and self.trace is not None:
            trace = self.trace
            self._trace_depth = trace[0, 2] - trace[:, 2]

        return self._trace_depth

    @property
    def _from(self):
        data_obj = self.get_data("FROM")
        if data_obj:
            return data_obj[0]
        return None

    @property
    def _to(self):
        data_obj = self.get_data("TO")
        if data_obj:
            return data_obj[0]
        return None

    @property
    def _depth(self):
        data_obj = self.get_data("DEPTH")
        if data_obj:
            return data_obj[0]
        return None

    def add_data(self, data: dict, property_group: str = None) -> Data | list[Data]:
        """
        Create :obj:`~geoh5py.data.data.Data` specific to the drillhole object
        from dictionary of name and arguments. A keyword 'depth' or 'from-to'
        with corresponding depth values is expected in order to locate the
        data along the well path.

        :param data: Dictionary of data to be added to the object, e.g.

        .. code-block:: python

            data_dict = {
                "data_A": {
                    'values', [v_1, v_2, ...],
                    "from-to": numpy.ndarray,
                    },
                "data_B": {
                    'values', [v_1, v_2, ...],
                    "depth": numpy.ndarray,
                    },
            }

        :return: List of new Data objects.
        """
        data_objects = []

        for name, attr in data.items():
            assert isinstance(attr, dict), (
                f"Given value to data {name} should of type {dict}. "
                f"Type {type(attr)} given instead."
            )
            assert "values" in list(
                attr.keys()
            ), f"Given attr for data {name} should include 'values'"

            attr["name"] = name

            if "collocation_distance" in attr.keys():
                assert (
                    attr["collocation_distance"] > 0
                ), "Input depth 'collocation_distance' must be >0."
                collocation_distance = attr["collocation_distance"]
            else:
                collocation_distance = self.default_collocation_distance

            if "depth" in attr.keys():
                attr["association"] = "VERTEX"
                attr["values"] = self.validate_log_data(
                    attr["depth"],
                    attr["values"],
                    collocation_distance=collocation_distance,
                )
                del attr["depth"]
            elif "from-to" in attr.keys():
                attr["association"] = "CELL"
                attr["values"] = self.validate_interval_data(
                    attr["from-to"],
                    attr["values"],
                    collocation_distance=collocation_distance,
                )
                del attr["from-to"]
            else:
                assert attr["association"] == "OBJECT", (
                    "Input data dictionary must contain {key:values} "
                    + "{'depth':numpy.ndarray}, {'from-to':numpy.ndarray} "
                    + "or {'association': 'OBJECT'}."
                )

            entity_type = self.validate_data_type(attr)
            kwargs = {"parent": self, "association": attr["association"]}
            for key, val in attr.items():
                if key in ["parent", "association", "entity_type", "type"]:
                    continue
                kwargs[key] = val

            data_object = self.workspace.create_entity(
                Data, entity=kwargs, entity_type=entity_type
            )

            if property_group is not None:
                self.add_data_to_group(data_object, property_group)

            data_objects.append(data_object)

        # Check the depths and re-sort data if necessary
        self.sort_depths()
        self.workspace.finalize()
        if len(data_objects) == 1:
            return data_object

        return data_objects

    def desurvey(self, depths):
        """
        Function to return x, y, z coordinates from depth.
        """
        assert (
            self.surveys is not None and self.collar is not None
        ), "'surveys' and 'collar' attributes required for desurvey operation"

        if isinstance(depths, list):
            depths = np.asarray(depths)

        ind_loc = np.maximum(
            np.searchsorted(self.surveys[:, 0], depths, side="left") - 1,
            0,
        )
        ind_dev = np.minimum(ind_loc, self.deviation_x.shape[0] - 1)
        locations = (
            self.locations[ind_loc, :]
            + (depths - self.surveys[ind_loc, 0])[:, None]
            * np.c_[
                self.deviation_x[ind_dev],
                self.deviation_y[ind_dev],
                self.deviation_z[ind_dev],
            ]
        )
        return locations

    def add_vertices(self, xyz):
        """
        Function to add vertices to the drillhole
        """
        indices = np.arange(xyz.shape[0])
        if self.n_vertices is None:
            self.vertices = xyz
        else:
            indices += self.vertices.shape[0]
            self.vertices = np.vstack([self.vertices, xyz])

        return indices.astype("uint32")

    def validate_log_data(self, depth, input_values, collocation_distance=1e-4):
        """
        Compare new and current depth values, append new vertices if necessary and return
        an augmented values vector that matches the vertices indexing.
        """
        assert len(depth) == len(input_values), (
            f"Mismatch between input 'depth' shape{depth.shape} "
            + f"and 'values' shape{input_values.shape}"
        )

        input_values = np.r_[input_values]

        if self._depth is None:
            self.workspace.create_entity(
                Data,
                entity={
                    "parent": self,
                    "association": "VERTEX",
                    "name": "DEPTH",
                },
                entity_type={"primitive_type": "FLOAT"},
            )

        if self._depth.values is None:  # First data appended
            self.add_vertices(self.desurvey(depth))
            depth = np.r_[np.ones(self.n_vertices - depth.shape[0]) * np.nan, depth]
            values = np.r_[
                np.ones(self.n_vertices - input_values.shape[0]) * np.nan, input_values
            ]
            self._depth.values = depth

        else:
            depths, indices = merge_arrays(
                self._depth.values,
                depth,
                return_mapping=True,
                collocation_distance=collocation_distance,
            )
            values = merge_arrays(
                np.ones(self.n_vertices) * np.nan,
                input_values,
                replace="B->A",
                mapping=indices,
            )
            self.add_vertices(self.desurvey(np.delete(depth, indices[:, 1])))
            self._depth.values = depths
            self.workspace.finalize()

        return values

    def validate_interval_data(self, from_to, input_values, collocation_distance=1e-4):
        """
        Compare new and current depth values, append new vertices if necessary and return
        an augmented values vector that matches the vertices indexing.
        """
        if isinstance(from_to, list):
            from_to = np.vtack(from_to)

        assert from_to.shape[0] == len(input_values), (
            f"Mismatch between input 'from_to' shape{from_to.shape} "
            + f"and 'values' shape{input_values.shape}"
        )
        assert from_to.shape[1] == 2, "The `from-to` values must have shape(*, 2)"

        if (self._from is None) and (self._to is None):
            uni_depth, inv_map = np.unique(from_to, return_inverse=True)
            self.cells = self.add_vertices(self.desurvey(uni_depth))[inv_map].reshape(
                (-1, 2)
            )
            self.workspace.create_entity(
                Data,
                entity={
                    "parent": self,
                    "association": "CELL",
                    "name": "FROM",
                    "values": from_to[:, 0],
                },
                entity_type={"primitive_type": "FLOAT"},
            )
            self.workspace.create_entity(
                Data,
                entity={
                    "parent": self,
                    "association": "CELL",
                    "name": "TO",
                    "values": from_to[:, 1],
                },
                entity_type={"primitive_type": "FLOAT"},
            )
        else:
            from_ind = match_values(
                self._from.values,
                from_to[:, 0],
                collocation_distance=collocation_distance,
            )
            to_ind = match_values(
                self._to.values,
                from_to[:, 1],
                collocation_distance=collocation_distance,
            )

            # Find matching cells
            in_match = np.ones((self._from.values.shape[0], 2)) * np.nan
            in_match[from_ind[:, 0], 0] = from_ind[:, 1]
            in_match[to_ind[:, 0], 1] = to_ind[:, 1]

            out_match = np.ones_like(from_to) * np.nan
            out_match[from_ind[:, 1], 0] = from_ind[:, 0]
            out_match[to_ind[:, 1], 1] = to_ind[:, 0]

            cell_map = np.c_[
                np.where(in_match[:, 0] == in_match[:, 1])[0],
                np.where(out_match[:, 0] == out_match[:, 1])[0],
            ]

            # Add vertices
            vert_new = np.ones_like(from_to, dtype="bool")
            vert_new[from_ind[:, 1], 0] = False
            vert_new[to_ind[:, 1], 1] = False
            ind_new = np.where(vert_new.flatten())[0]
            uni_new, inv_map = np.unique(
                from_to.flatten()[ind_new], return_inverse=True
            )

            # Add cells
            new_cells = np.ones_like(from_to.flatten()) * np.nan
            new_cells[ind_new] = self.add_vertices(self.desurvey(uni_new))[inv_map]
            new_cells = new_cells.reshape((-1, 2))
            new_cells[from_ind[:, 1], 0] = self.cells[from_ind[:, 0], 0]
            new_cells[to_ind[:, 1], 1] = self.cells[to_ind[:, 0], 1]
            new_cells = np.delete(new_cells, cell_map[:, 1], 0)

            # Append values
            input_values = merge_arrays(
                np.ones(self.n_cells) * np.nan,
                np.r_[input_values],
                replace="B->A",
                mapping=cell_map,
            )
            self._from.values = merge_arrays(
                self._from.values, from_to[:, 0], mapping=cell_map
            )
            self._to.values = merge_arrays(
                self._to.values, from_to[:, 1], mapping=cell_map
            )
            self.cells = np.r_[self.cells, new_cells.astype("uint32")]

        return input_values

    def sort_depths(self):
        """
        Read the 'DEPTH' data and sort all Data.values if needed
        """
        if self.get_data("DEPTH"):
            data_obj = self.get_data("DEPTH")[0]
            depths = data_obj.check_vector_length(data_obj.values)
            if not np.all(np.diff(depths) >= 0):
                sort_ind = np.argsort(depths)

                for child in self.children:
                    if isinstance(child, Data) and child.association.name == "VERTEX":
                        child.values = child.check_vector_length(child.values)[sort_ind]

                if self.vertices is not None:
                    self.vertices = self.vertices[sort_ind, :]

                if self.cells is not None:
                    key_map = np.argsort(sort_ind)[self.cells.flatten()]
                    self.cells = key_map.reshape((-1, 2)).astype("uint32")

        self.workspace.finalize()
