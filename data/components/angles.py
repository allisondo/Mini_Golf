
from math import pi, hypot, cos, sin, atan2


def get_distance(origin, destination):
    return hypot(destination[0] - origin[0],
                 destination[1] - origin[1])


def get_angle(origin, destination):
    x_dist = destination[0] - origin[0]
    y_dist = destination[1] - origin[1]
    return atan2(-y_dist, x_dist) % (2 * pi)


def get_xaxis_reflection(origin, destination):
    x_dist = origin[0] - destination[0]
    y_dist = origin[1] - destination[1]
    return atan2(-y_dist, -x_dist) % (2 * pi)


def get_yaxis_reflection(origin, destination):
    x_dist = origin[0] - destination[0]
    y_dist = origin[1] - destination[1]
    return atan2(y_dist, x_dist) % (2 * pi)


def get_opposite_angle(origin, destination):
    x_dist = origin[0] - destination[0]
    y_dist = origin[1] - destination[1]
    return atan2(-y_dist, x_dist) % (2 * pi)


def project(pos, angle, distance):
    return (pos[0] + (cos(angle) * distance),
            pos[1] - (sin(angle) * distance))
