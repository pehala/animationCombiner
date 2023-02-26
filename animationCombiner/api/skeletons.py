from functools import cached_property
from typing import Dict, List

from animationCombiner.utils import Singleton


class Skeleton:
    """Skeleton represent parent-child relations between individual bones. Should always start at root"""

    def __init__(self, relations: Dict[str, List[str]]) -> None:
        self.relations = relations
        super().__init__()

    @cached_property
    def bones(self) -> List[str]:
        """List of bones in a hierarchical order (e.g. parent will always be done before a child)"""
        bones = ["root"]
        queue = ["root"]
        while len(queue) > 0:
            bone = queue.pop()
            if bone in self.relations:
                children = self.relations[bone]
                bones.extend(children)
                queue.extend(children)
        return bones

    def order(self) -> List[str]:
        return self.bones


class HBMSkeleton(Skeleton, metaclass=Singleton):
    """Skeleton from HBM05 data set"""

    def __init__(self) -> None:
        super().__init__(
            {
                "root": ["lowerback", "lhipjoint", "rhipjoint"],
                "lowerback": ["upperback"],
                "upperback": ["thorax"],
                "thorax": ["lowerneck", "lclavicle", "rclavicle"],
                "lowerneck": ["upperneck"],
                "upperneck": ["head"],
                "lclavicle": ["lhumerus"],
                "lhumerus": ["lradius"],
                "lradius": ["lwrist"],
                "lwrist": ["lhand", "lthumb"],
                "lhand": ["lfingers"],
                "rclavicle": ["rhumerus"],
                "rhumerus": ["rradius"],
                "rradius": ["rwrist"],
                "rwrist": ["rhand", "rthumb"],
                "rhand": ["rfingers"],
                "lhipjoint": ["lfemur"],
                "lfemur": ["ltibia"],
                "ltibia": ["lfoot"],
                "lfoot": ["ltoes"],
                "rhipjoint": ["rfemur"],
                "rfemur": ["rtibia"],
                "rtibia": ["rfoot"],
                "rfoot": ["rtoes"],
            }
        )
