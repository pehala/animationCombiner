from mathutils import Matrix

from animationCombiner.api.model import RawAnimation

invert_xz_matrix = Matrix([(1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)])


def invert_yz(animation: RawAnimation):
    """Provides in-place conversion between XYZ and XZY coordinate systems"""
    for pose in animation.poses:
        for position in pose.bones.values():
            position.rotate(invert_xz_matrix)
