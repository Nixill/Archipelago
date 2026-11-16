from typing import NamedTuple, TYPE_CHECKING

from BaseClasses import Region

from typing import NamedTuple, TYPE_CHECKING

from BaseClasses import Region

from .locations import create_locations
from .rules import create_rules

if TYPE_CHECKING:
    from ... import UFO50World


# not sure if we really need this yet, but making it in case we need it later since it's easy to remove
class RegionInfo(NamedTuple):
    rooms: list[str] = []  # rooms this region contains, for the purpose of the garden prize access rule

regions: list[str] = [
    "Menu",
    *[
        f"Race 0{i}"
        for i in range(1, 9)
    ],
    "Racers",
    "Scores",
]

def create_regions_and_rules(world: "UFO50World") -> dict[str, Region]:
    bbr_regions = dict[str, Region]()
    for region_name in regions:
        bbr_regions[region_name] = Region(f"The Big Bell Race - {region_name}", world.player, world.multiworld)

    create_locations(world, bbr_regions)
    create_rules(world, bbr_regions)

    return bbr_regions