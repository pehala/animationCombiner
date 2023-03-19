from mathutils import Vector

from animationCombiner.api.model import Pose


def normalize_pose(poses: list[Pose]) -> [list[Pose], list[Vector]]:
    """Normalizes the pose and returns both the new normalized pose and the translation vectors"""
    translations = []
    normalized = []
    for pose in poses:
        translation = pose.bones["root"].copy()
        translation.negate()
        translations.append(translation)
        normalized.append(Pose({bone: pos - translation for bone, pos in pose.bones.items()}))
    return normalized, translations