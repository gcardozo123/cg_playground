from pathlib import Path


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

    def get_vertex_at(self, index):
        return self._verts[index]

    def get_face_at(self, index):
        return self._faces[index]

    def num_faces(self):
        return len(self._faces)

    def num_verts(self):
        return len(self._verts)

    def load_from_obj(self, filename):
        """
        Parses a wavfront .obj file
        # List of geometric vertices, with (x, y, z [,w]) coordinates, w is optional and defaults to 1.0.
        v 0.123 0.234 0.345 1.0
        # List of texture coordinates, in (u, [v ,w]) coordinates, these will vary between 0 and 1, v and w are optional and default to 0.
        vt 0.500 1 [0]
        # List of vertex normals in (x,y,z) form; normals might not be unit vectors.
        vn 0.707 0.000 0.707
        # Parameter space vertices in ( u [,v] [,w] ) form; free form geometry statement ( see below )
        vp 0.310000 3.210000 2.100000
        # Polygonal face element (see below)
        f 1 2 3
        f 3/1 4/2 5/3
        # vertex/texture/normal indices which start at 1
        f 6/4/1 3/5/3 7/6/5
        f 7//1 8//2 9//3
        # Line element (see below)
        l 5 8 1 2 4 9
        """
        filename = Path(filename)
        with open(filename, mode='r') as f:
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
                vertices = line_split[1:]
                # for now let's just get the vertex index. I'm using -1 because they're 1-based T-T
                vertex_indexes = tuple([int(v.split("/")[0]) - 1 for v in vertices])
                self._faces.append(vertex_indexes)


