from math import acos, sqrt
from typing import Sequence


class Vec2:
    """
    I know, you're reading this and thinking "WTF? Why is he not using numpy for this?", it's
    because I want to refresh my basic math skills.
    """

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self == other)

    def add(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def sub(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def magnitude(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        mag = self.magnitude()
        return Vec2(self.x / mag, self.y / mag)

    def angle_to(self, other):
        """
        Returns the radian angles to other Vec2
        """
        dot_prod = self.dot(other)
        mag = self.magnitude()
        other_mag = other.magnitude()
        return acos(dot_prod / (mag * other_mag))

    @classmethod
    def obtain_barycentric_weights(cls, p, v0, v1, v2):
        """
        Returns the barycentric weights (reference: https://codeplea.com/triangular-interpolation)
        for a given point `p` inside a triangle (v0, v1, v2).
        """
        denominator = (v1.y - v2.y) * (v0.x - v2.x) + (v2.x - v1.x) * (v0.y - v2.y)
        if denominator == 0:
            return (-1, -1, -1)

        w1 = ((v1.y - v2.y) * (p.x - v2.x) + (v2.x - v1.x) * (p.y - v2.y)) / denominator
        w2 = ((v2.y - v0.y) * (p.x - v2.x) + (v0.x - v2.x) * (p.y - v2.y)) / denominator
        w3 = 1 - w1 - w2
        return (w1, w2, w3)


class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not (self == other)

    def add(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def sub(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def magnitude(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalized(self):
        mag = self.magnitude()
        return Vec3(self.x / mag, self.y / mag, self.z / mag)

    def angle_to(self, other):
        """
        Returns the radian angles to other Vec2
        """
        dot_prod = self.dot(other)
        mag = self.magnitude()
        other_mag = other.magnitude()
        return acos(dot_prod / (mag * other_mag))

    def distance(self, other):
        _dx, _dy, _dz = self.dx(other), self.dy(other), self.dz(other)
        return sqrt(_dx * _dx + _dy * _dy + _dz * _dz)

    def distance_2d(self, other):
        _dx, _dy = self.dx(other), self.dy(other)
        return sqrt(_dx * _dx + _dy * _dy)

    def dx(self, other):
        return abs(self.x - other.x)

    def dy(self, other):
        return abs(self.y - other.y)

    def dz(self, other):
        return abs(self.z - other.z)

    @classmethod
    def clone(cls, other):
        return Vec3(other.x, other.y, other.z)

    @classmethod
    def triangle_area(cls, p0, p1, p2):
        """
        Returns twice the area - just to avoid division - of the oriented triangle (p0, p1, p2).
        The area is positive if the triangle is oriented counterclockwise.
        """
        return (p1.x - p0.x) * (p2.y - p0.y) - (p1.y - p0.y) * (p2.x - p0.x)

    @classmethod
    def is_counterclockwise(cls, p0, p1, p2):
        """
        Returns true if the Vec2s p0, p1, p2 are in a counterclockwise order
        """
        return Vec3.triangle_area(p0, p1, p2) > 0


def apply_weights(values: Sequence[float], weights: Sequence[float]):
    """
    Returns values[0] * weights[0] + values[1] * weights[1] + ... + values[n] * weights[n]
    """
    return sum([v[0] * v[1] for v in zip(values, weights)])
