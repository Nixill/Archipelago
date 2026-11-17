from typing import TYPE_CHECKING

from BaseClasses import Region, CollectionState
from worlds.generic.Rules import set_rule

from . import racers

if TYPE_CHECKING:
    from ... import UFO50World

# This was originally temporary for debugging but it became permanent.
class RaceInLogicRule:
    race_num: int
    world: "UFO50World"

    def __init__(self, race_num: int, world: "UFO50World"):
        self.race_num = race_num
        self.world = world

    def __repr__(self) -> str:
        return f"RaceInLogicRule({self.race_num}, <world>)"

    def __call__(self, state: CollectionState) -> bool:
        if state.has(f"The Big Bell Race - Race 0{self.race_num}", self.world.player):
            return True
        if state.count(f"The Big Bell Race - Progressive Racetrack", self.world.player) >= self.race_num:
            return True
        return False

class RacerInLogicRule:
    racer: str
    world: "UFO50World"

    def __init__(self, racer: str, world: "UFO50World"):
        self.racer = racer
        self.world = world

    def __repr__(self) -> str:
        return f"RacerInLogicRule({self.racer.__repr__()}, <world>)"

    def __call__(self, state: CollectionState) -> bool:
        if not self.world.options.bbr_racer_checks.value:
            return True
        if state.has(f"The Big Bell Race - {self.racer}", self.world.player):
            return True
        return False

class ScoreInLogicRule:
    score: int
    world: "UFO50World"

    def __init__(self, score: int, world: "UFO50World"):
        self.score = score
        self.world = world

    def __repr__(self) -> str:
        return f"ScoreInLogicRule({self.score}, <world>)"

    def __call__(self, state: CollectionState) -> bool:
        return max_score_in_logic(state, self.world) >= self.score

def powerup_count(state: CollectionState, world: "UFO50World") -> int:
    return state.count_group_unique("The Big Bell Race - Power-Ups", world.player)

def race_count(state: CollectionState, world: "UFO50World") -> int:
    if world.options.bbr_race_progression.value == world.options.bbr_race_progression.option_randomized:
        return state.count_group_unique("The Big Bell Race - Randomized Tracks", world.player)
    else:
        return state.count("The Big Bell Race - Progressive Racetrack", world.player)

def max_score_in_logic(state: CollectionState, world: "UFO50World") -> int:
    races = race_count(state, world)
    if powerup_count(state, world) == 5:
        score_per_race = 9
    else:
        score_per_race = world.options.bbr_logical_points_per_race.value

    return score_per_race * races

def is_cherry_in_logic(state: CollectionState, world: "UFO50World") -> bool:
    if race_count(state, world) < 8:
        return False
    if world.options.bbr_cherry_availability.value == world.options.bbr_cherry_availability.option_always_available:
        return True
    if powerup_count(state, world) >= 5:
        return True
    return False

def is_gold_in_logic(state: CollectionState, world: "UFO50World") -> bool:
    gold_races_needed = max(
        world.options.bbr_gold_availability.value,
        world.options.bbr_gold_logic.value
    )
    return race_count(state, world) >= gold_races_needed

def create_rules(world: "UFO50World", regions: dict[str, Region]) -> None:
    for i in range(1, 9):
        regions["Menu"].connect(regions[f"Race 0{i}"],
                                rule=RaceInLogicRule(i, world))
                                # rule=lambda state: is_race_in_logic(i, state, world))

    if world.options.bbr_racer_checks.value:
        regions["Menu"].connect(regions["Racers"])
        for racer in racers:
            set_rule(world.get_location(f"The Big Bell Race - Win with {racer}"),
                     rule=RacerInLogicRule(racer, world))

    regions["Menu"].connect(regions["Scores"])
    for i in range(1, 72):
        if str(i) in world.options.bbr_score_checks:
            set_rule(world.get_location(f"The Big Bell Race - Score {i}"),
                     rule=ScoreInLogicRule(i, world))

    # Garden is sphere 1

    set_rule(world.get_location("The Big Bell Race - Gold"),
             rule=lambda state: is_gold_in_logic(state, world))

    if "The Big Bell Race" in world.options.cherry_allowed_games:
        set_rule(world.get_location("The Big Bell Race - Cherry"),
                 rule=lambda state: is_cherry_in_logic(state, world))
