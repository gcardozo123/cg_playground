from math import acos, sqrt


class Vec2:
    """
    I know, you're reading this and thinking "WTF? Why is he not using numpy for this?", it's
    because I want to refresh my basic math skills.
    """

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

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


class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

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
