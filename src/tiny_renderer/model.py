from pathlib import Path
from typing import List

from math_utils import Vec2, Vec3


class Model:
    """
    Represents a 3D model
    """

    VERTEX = "v"
    UV = "vt"
    NORMAL = "vn"
    PARAMETER = "vp"
    FACE = "f"

    def __init__(self):
        self._verts = []
        self._faces = []
        # texture coordinates for each vertex of a face (triangle), each index here,  refers to a
        # (u,v) coordinate in `self._uvs`
        self._texture_coordinates_indexes = []
        self._uvs = []
        self._normals = []
        # list of tuples where each tuple contains 3 indexes representing positions at `self._normals`
        # where the actual normals of a given vertex (from a given face) is stored
        self._normal_indexes = []

    def get_vertex_at(self, index):
        return self._verts[index]

    def get_face_at(self, index):
        return self._faces[index]

    def get_normal_as_vec3(self, index):
        return self._normals[index]

    def get_normals_from_face(self, face_index) -> List[Vec3]:
        """
        Returns a list of normals (they're already unitary vectors)
        """
        indexes = self._normal_indexes[face_index]
        return [self._normals[i] for i in indexes]

    def get_uv_at(self, index):
        return self._uvs[index]

    def get_texture_coordinate_index_at(self, index):
        return self._texture_coordinates_indexes[index]

    def get_uvs_from_face(self, index) -> List[tuple]:
        """
        Returns a list of (u,v) tuples for each vertex of face indexed by `index`
        """
        indexes = self.get_texture_coordinate_index_at(index)
        return [self._uvs[i] for i in indexes]

    def num_faces(self):
        return len(self._faces)

    def num_verts(self):
        return len(self._verts)

    def num_texture_coordinates_indexes(self):
        return len(self._texture_coordinates_indexes)

    def num_uvs(self):
        return len(self._uvs)

    def load_from_obj(self, filename):
        """
        Parses a wavfront .obj file. The file is parsed considering the following elements:

        List of geometric vertices, with (x, y, z [,w]) coordinates, w is optional and defaults to 1.0:
        v 0.123 0.234 0.345 1.0

        List of texture coordinates, in (u, [v, w]) coordinates, these will vary between 0 and 1,
        v and w are optional and default to 0:
        vt 0.500 1 [0]

        List of vertex normals in (x, y, z) form; normals might not be unit vectors:
        vn 0.707 0.000 0.707

        Parameter space vertices in ( u [,v] [,w] ) form; free form geometry statement:
        vp 0.310000 3.210000 2.100000

        Polygonal face element:
        f 1 2 3
        f 3/1 4/2 5/3

        vertex/texture/normal indices which start at 1:
        f 6/4/1 3/5/3 7/6/5
        f 7//1 8//2 9//3

        Line element:
        l 5 8 1 2 4 9
        """
        filename = Path(filename)
        with open(filename, mode="r") as f:
            lines = f.readlines()

        for line in lines:
            line_split = line.split()
            if not line_split:
                continue
            line_type = line_split[0]

            if line_type == Model.VERTEX:
                self._verts.append(
                    (float(line_split[1]), float(line_split[2]), float(line_split[3]))
                )
            elif line_type == Model.FACE:
                vert_tex_norm = line_split[1:]  # vertex/texture/normal
                assert len(vert_tex_norm) == 3

                # Using -1 because they're 1-based:
                vertex_indexes = tuple([int(v.split("/")[0]) - 1 for v in vert_tex_norm])
                self._faces.append(vertex_indexes)

                texture_coordinates = tuple([int(tex.split("/")[1]) - 1 for tex in vert_tex_norm])
                self._texture_coordinates_indexes.append(texture_coordinates)

                normal_indexes = tuple([int(n.split("/")[2]) - 1 for n in vert_tex_norm])
                self._normal_indexes.append(normal_indexes)
            elif line_type == Model.UV:
                u, v, _ = line_split[1:]
                self._uvs.append(Vec2(float(u), float(v)))
            elif line_type == Model.NORMAL:
                self._normals.append(
                    Vec3(
                        float(line_split[1]), float(line_split[2]), float(line_split[3])
                    ).normalized()
                )
