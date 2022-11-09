def increase_angle(angle: float, increase_in_degrees: float) -> float:
    angle += increase_in_degrees

    if angle > 360:
        angle %= 360
    elif angle < -360:
        angle %= -360

    return angle
