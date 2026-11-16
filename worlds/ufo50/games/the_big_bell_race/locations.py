from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Region, Location, Item, ItemClassification
from worlds.generic.Rules import add_rule

from . import racers

from ...constants import get_game_base_id

if TYPE_CHECKING:
    from ... import UFO50World


class LocationInfo(NamedTuple):
    id_offset: int
    region_name: str

location_table = dict[str, LocationInfo]([
    *((f"Race 0{i} - Win", LocationInfo(i * 10, f"Race 0{i}")) for i in range(1, 9)),
    *((f"Race 0{i} - Collect Item", LocationInfo(i * 10 + 1, f"Race 0{i}")) for i in range(1, 9)),
    *((f"Win with {name}", LocationInfo(100 + i, "Racers")) for i, name in enumerate(racers)),
    *((f"Score {i}", LocationInfo(200 + i, "Scores")) for i in range(1, 72)),

    ("Garden", LocationInfo(997, "Menu")),
    ("Gold", LocationInfo(998, "Menu")),
    ("Cherry", LocationInfo(999, "Menu")),
])

def get_locations() -> dict[str, int]:
    return {
        f"The Big Bell Race - {name}": data.id_offset + get_game_base_id("The Big Bell Race")
        for name, data in location_table.items()
    }

def get_location_groups() -> dict[str, set[str]]:
    return {
        "The Big Bell Race": set(location_table.keys()),
        "The Big Bell Race - Race Wins": {
            f"The Big Bell Race - Race 0{i} - Win"
            for i in range(1, 9)
        },
        "The Big Bell Race - Race Items": {
            f"The Big Bell Race - Race 0{i} - Collect Item"
            for i in range(1, 9)
        },
        **{
            f"The Big Bell Race - Race 0{i}": {
                f"The Big Bell Race - Race 0{i} - Win",
                f"The Big Bell Race - Race 0{i} - Collect Item",
            }
            for i in range(1, 9)
        },
        "The Big Bell Race - Racer Wins": {
            f"The Big Bell Race - Win with {name}"
            for name in racers
        },
        "The Big Bell Race - Scores": {
            f"The Big Bell Race - Score {i}"
            for i in range(1, 72)
        },
    }

def create_locations(world: "UFO50World", regions: dict[str, Region]) -> None:
    for loc_name, loc_data in location_table.items():
        if loc_name in racers and not world.options.bbr_racer_checks.value:
            continue

        if loc_name.startswith("Score ") and loc_name.removeprefix("Score ") not in world.options.bbr_score_checks:
            continue

        if loc_name == "Cherry" and "The Big Bell Race" not in world.options.cherry_allowed_games:
            break

        if loc_name in ["Gold", "Cherry"] and "The Big Bell Race" in world.goal_games:
            if (loc_name == "Gold" and "The Big Bell Race" not in world.options.cherry_allowed_games) or loc_name == "Cherry":
                loc = Location(world.player, f"The Big Bell Race - {loc_name}", None, regions[loc_data.region_name])
                loc.place_locked_item(Item("Completed The Big Bell Race", ItemClassification.progression, None, world.player))
                add_rule(world.get_location("Completed All Games"), lambda state: state.has("Completed The Big Bell Race", world.player))
                regions[loc_data.region_name].locations.append(loc)
                break

        loc = Location(world.player, f"The Big Bell Race - {loc_name}", get_game_base_id("The Big Bell Race") + loc_data.id_offset,
                       regions[loc_data.region_name])
        regions[loc_data.region_name].locations.append(loc)