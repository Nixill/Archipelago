from typing import TYPE_CHECKING, Iterable, NamedTuple, Optional

from BaseClasses import ItemClassification as IC, Item

from . import racers
from ...constants import get_game_base_id

if TYPE_CHECKING:
    from ... import UFO50World

class ItemInfo(NamedTuple):
    id_offset: int
    classification: IC
    quantity: int = 1

class _FlatItemInfo(NamedTuple):
    category: str
    name: str
    @property
    def full_name(self) -> str:
        if self.category: return f"The Big Bell Race - {self.category} - {self.name}"
        else: return f"The Big Bell Race - {self.name}"
    data: ItemInfo

item_table: dict[str, dict[str, ItemInfo]] = {
    "Progressive Tracks": {
        "Progressive Racetrack": ItemInfo(0, IC.progression, 7),
    },
    "Randomized Tracks": {
        "Race 01": ItemInfo(1, IC.progression),
        "Race 02": ItemInfo(2, IC.progression),
        "Race 03": ItemInfo(3, IC.progression),
        "Race 04": ItemInfo(4, IC.progression),
        "Race 05": ItemInfo(5, IC.progression),
        "Race 06": ItemInfo(6, IC.progression),
        "Race 07": ItemInfo(7, IC.progression),
        "Race 08": ItemInfo(8, IC.progression),
    },
    "Racers": {
        racer: ItemInfo(100 + i, IC.progression)
        for i, racer in enumerate(racers)
    },
    "Power-Ups": {
        "Guns": ItemInfo(200, IC.progression),
        "Mines": ItemInfo(201, IC.progression),
        "Fireballs": ItemInfo(202, IC.progression),
        "Slash": ItemInfo(203, IC.progression),
        "Payload": ItemInfo(204, IC.progression),
    },
    # These are intentionally zero quantity! The filler function can take care of them.
    "Fillers": {
        "Explode": ItemInfo(300, IC.trap, 0),
        "Remove a Lap": ItemInfo(301, IC.filler, 0),
        "Add a Lap": ItemInfo(302, IC.filler, 0),
        "Explode Random Opponent": ItemInfo(303, IC.useful, 0),
    },
}

flat_item_table: dict[str, ItemInfo] = {
    name: data
    for items in item_table.values()
    for name, data in items.items()
}

# this is for filling out item_name_to_id, it should be static regardless of yaml options
def get_items() -> dict[str, int]:
    return {
        f"The Big Bell Race - {name}": data.id_offset + get_game_base_id("The Big Bell Race")
        for name, data in flat_item_table.items()
    }

# this should return the item groups for this game, independent of yaml options
def get_item_groups() -> dict[str, set[str]]:
    return {
        "The Big Bell Race": set(flat_item_table.keys()),
        **{
            f"The Big Bell Race - {category}": {
                f"The Big Bell Race - {name}" for name in items.keys()
            }
            for category, items in item_table.items()
        }
    }

# for when the world needs to create an item at random (like with random filler items)
def create_item(item_name: str, world: "UFO50World", item_class: IC = None) -> Item:
    base_id = get_game_base_id("The Big Bell Race")
    item_name = item_name.removeprefix("The Big Bell Race - ")
    item_data = flat_item_table[item_name]
    return Item(f"The Big Bell Race - {item_name}", item_class or item_data.classification,
                base_id + item_data.id_offset, world.player)

# for when the world is getting the items to place into the multiworld's item pool
def create_items(world: "UFO50World") -> list[Item]:
    items_to_create: dict[str, int] = {item_name: data.quantity for item_name, data in flat_item_table.items()}

    # First build the precollected items list
    precollected_items = set[str]()

    for item in world.multiworld.precollected_items[world.player]:
        item_name = item.name
        if item_name.startswith("The Big Bell Race - "):
            item_name = item_name.removeprefix("The Big Bell Race - ")
            precollected_items.add(item_name)

    # Parse options first

    # Whether we're creating Individual Tracks or Progressive Tracks
    if world.options.bbr_race_progression.value == world.options.bbr_race_progression.option_randomized:
        items_to_create["Progressive Racetrack"] = 0
        # Find any precollected tracks (i.e. starting inventory):
        precollected_races = {i.removeprefix("Race ") for i in precollected_items if i.startswith("Race ")}
        if precollected_races:
            for race in precollected_races:
                items_to_create[f"Race {race}"] = 0
        else:
            starting_race = world.random.randint(1, 8)
            items_to_create[f"Race 0{starting_race}"] = 0
            race_item = create_item(f"Race 0{starting_race}", world)
            world.multiworld.push_precollected(race_item)
    else:
        for i in range(1, 9):
            items_to_create[f"Race 0{i}"] = 0
        world.multiworld.push_precollected(create_item(f"Progressive Racetrack", world))

    # Are we collecting racers?
    if world.options.bbr_racer_checks.value:
        # Find any precollected racers (i.e. starting inventory):
        precollected_racers = {i for i in precollected_items if i in racers}
        if precollected_racers:
            for racer in precollected_racers:
                items_to_create[racer] = 0
        else:
            starting_racer = world.random.choice(racers)
            items_to_create[starting_racer] = 0
            racer_item = create_item(starting_racer, world)
            world.multiworld.push_precollected(racer_item)
    else:
        for racer in racers:
            items_to_create[racer] = 0

    # Output the list now (no fillers, we'll take care of that later!)
    bbr_items = list[Item]()
    for item_name, quantity in items_to_create.items():
        for _ in range(quantity):
            bbr_items.append(create_item(item_name, world))
    return bbr_items

def get_filler_item_name(world: "UFO50World") -> str:
    bbr_name = "The Big Bell Race - "
    bbr_fillers = [n
                   for n, v in item_table["Fillers"].items()
                     if v.classification & (IC.trap == 0) or world.options.bbr_traps_enabled.value]
    return bbr_name + world.random.choice(bbr_fillers)
