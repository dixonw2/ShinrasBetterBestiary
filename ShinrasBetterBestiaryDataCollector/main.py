import math

import mwparserfromhell
import requests
import re
import json

from bestiary_entry import BestiaryEntry, ViaInfinito, LootTable, ItemDrop, BattleData

url = "https://finalfantasy.fandom.com/api.php"

NORMAL = "Normal"
OVERSOUL = "Oversoul"
FIEND_ARENA = "Fiend Arena"
FIEND_ARENA_OVERSOUL = "Fiend Arena Oversoul"


def clean_wikitext(value) -> str:
    code = mwparserfromhell.parse(value)
    return code.strip_code().strip()


def parse_list(value) -> list[str]:
    return [
        clean_wikitext(x).strip() for x in re.split(r"<br\s*/?>|,", value) if x.strip()
    ]


def parse_chapter_list(value: str) -> list[int] | None:
    chapters = []

    for part in re.split(r"<br\s*/?>", value):
        if "(Fiend Arena)" in part:
            continue
        chapters.extend(parse_int_list(part))

    return chapters


def parse_locations_list(value: str) -> list[str]:
    locations = []
    for part in parse_list(value):
        if "Fiend Arena" in part:
            continue

        locations.append(part)

    return locations


def parse_int_list(value: str) -> list[int]:
    return [int(x) for x in re.findall(r"\d+", value)]


def parse_item(value) -> ItemDrop:
    cleaned = clean_wikitext(value)
    match = re.match(r"(.+?)\s+x(\d+)$", cleaned)

    if not match:
        return ItemDrop(item=cleaned, quantity=1)

    return ItemDrop(item=match.group(1).strip(), quantity=int(match.group(2)))


def parse_immunity(value) -> bool:
    if value == "Immune":
        return True

    return False


def parse_elemental_resistances(value) -> int:
    match value:
        case "Weak":
            return 2
        case "Immune":
            return 0
        case "Absorb":
            return -1
        case _:
            return 1


def parse_rate(value) -> float:
    if not value:
        return 1.0

    return int(value) / 256


def parse_via_infinito_floors(value: str) -> ViaInfinito | None:
    location = get_via_infinito_from_list(parse_list(value))

    if location is None:
        return None

    # Ignore boss entries
    if "(boss)" in location.lower():
        return None

    # Remove known prefixes
    location = re.sub(
        r"^(Via Infinito Floors |Via Infinito |Cloisters )",
        "",
        location,
        flags=re.IGNORECASE,
    )

    # Remove everything in parentheses
    location = re.sub(r"\s*\([^)]*\)", "", location).strip()

    # Normalize dash types
    location = location.replace("–", "-")

    numbers = [int(x) for x in re.findall(r"\d+", location)]

    if len(numbers) == 1:
        return ViaInfinito(min=numbers[0], max=numbers[0])

    if len(numbers) >= 2:
        return ViaInfinito(min=numbers[0], max=numbers[1])

    return None


def get_via_infinito_from_list(locations: list[str]) -> str | None:
    for location in locations:
        lower = location.lower()

        if (
            lower.startswith("via infinito")
            or lower.startswith("cloisters")
            or lower.endswith("(normal enemy)")
        ):
            return location

    return None


def parse_eject(value: str) -> int | bool:
    if value == "Immune":
        return False

    if not value:
        return 0

    return int(value)


def parse_death(value: str) -> int | bool:
    if value == "Immune":
        return False

    return int(value)


def parse_zantetsu(value: str) -> int:
    if not value:
        return 0

    return int(value)


def parse_stat(value: str) -> int:
    num = value.replace(",", "")

    # wiki is wrong for Elder Drake
    if num == "135 - 400+":
        num = "402"
    if "(INT & HD)" in num:
        match = re.search(r"/(\d+)", num)
        if match:
            num = match.group(1)

    return int(num)


def parse_oversoul(value: str) -> int:
    # some pages use a boolean for count for some reason
    # -1000 is an error value, must change manually
    if value in ["true", "false"]:
        return -1000

    return int(value)


FIELDS = {
    "bestiary": ("bestiary_index", int),
    "name": ("name", str),
    "species": ("species", clean_wikitext),
    "location": ("locations", parse_list),
    "locations": ("locations", parse_list),
    "blue bullet": ("blue_bullet", parse_list),
    "chapter": ("chapters", parse_chapter_list),
    "chapters": ("chapters", parse_chapter_list),
    "scan desc": ("scan_description", str),
    "level": ("level", int),
    "hp": ("hp", int),
    "mp": ("mp", parse_stat),
    "strength": ("strength", int),
    "magic": ("magic", int),
    "defense": ("defense", int),
    "mag defense": ("magic_defense", int),
    "agility": ("agility", int),
    "accuracy": ("accuracy", int),
    "evasion": ("evasion", int),
    "luck": ("luck", int),
    "exp": ("exp", int),
    "ap": ("ap", int),
    "gil": ("gil", int),
    "steal gil": ("pilfer_gil", int),
    "zantetsu": ("zantetsu", parse_zantetsu),
    "gravity": ("gravity", parse_immunity),
    "death": ("death", parse_death),
    "petrify": ("petrification", parse_immunity),
    "sleep": ("sleep", parse_immunity),
    "silence": ("silence", parse_immunity),
    "darkness": ("darkness", parse_immunity),
    "poison": ("poison", parse_immunity),
    "confuse": ("confusion", parse_immunity),
    "berserk": ("berserk", parse_immunity),
    "curse": ("curse", parse_immunity),
    "eject": ("eject", parse_eject),
    "stop": ("stop", parse_immunity),
    "doom": ("doom", parse_immunity),
    "delay": ("delay", parse_immunity),
    "slow": ("slow", parse_immunity),
    "interrupt": ("action_cancel", parse_immunity),
    "multi attack": ("multi_attack", parse_immunity),
    "abilities": ("abilities", parse_list),
    "teams": ("teams", parse_list),
    "clear": ("clear", str),
    "str mod": ("str_down", parse_immunity),
    "mag mod": ("mag_down", parse_immunity),
    "def mod": ("def_down", parse_immunity),
    "mdef mod": ("mag_def_down", parse_immunity),
    "luck mod": ("luck_down", parse_immunity),
    "eva mod": ("eva_down", parse_immunity),
    "accu mod": ("accu_down", parse_immunity),
    "fract damage": ("fract_damage", parse_immunity),
    "fire": ("fire", parse_elemental_resistances),
    "ice": ("ice", parse_elemental_resistances),
    "lightning": ("lightning", parse_elemental_resistances),
    "water": ("water", parse_elemental_resistances),
    "holy": ("holy", parse_elemental_resistances),
    "oversoul": ("oversoul_amount", parse_oversoul),
    "pod size": ("pod_size", str),
    "physical": ("physical", parse_immunity),
    "reflect": ("reflect", parse_immunity),
}

SKIPS = [
    "sec 1",
    "sec 2",
    "sec 3",
    "sec 4",
    "prev",
    "1 prev",
    "2 prev",
    "prev no",
    "next",
    "1 next",
    "2 next",
]

SECTIONS = ["sec 1", "sec 2", "sec 3", "sec 4"]


def get_data(data: dict, shared_data: dict):
    if data:
        return shared_data | data

    return {}


def build_entry(name: str, params) -> BestiaryEntry:
    normal = {}
    oversoul = {}
    creature_creator = {}
    fiend_arena = {}
    fiend_arena_oversoul = {}
    shared = {}

    current_section = NORMAL
    for param in params:
        key = str(param.name).strip()
        value = str(param.value).strip()

        # Chocobo is a special case--------------------------------------------------------------------------------------------------------

        if key in SKIPS:
            if key in SECTIONS:
                current_section = value
            continue

        if current_section not in [NORMAL, OVERSOUL, FIEND_ARENA, FIEND_ARENA_OVERSOUL]:
            raise ValueError

        if "cc " in key or key == "teams":
            # creature locations, chapters don't change but API can return cc location, 1 cc location, 2 cc location
            if "location" in key and "location" not in creature_creator:
                creature_creator["location"] = value
            elif "chapters" in key and "chapters" not in creature_creator:
                creature_creator["chapters"] = value
            elif key == "teams" and "teams" not in creature_creator:
                creature_creator["teams"] = value
        elif current_section == NORMAL and key.startswith("1 "):
            # normal non-shared data starts with "1 "
            normal[key[2:]] = value
        elif key in ["pod size", "1 pod size", "2 pod size"]:
            # creature size doesn't change but API can return pod size, 1 pod size, and 2 pod size
            creature_creator["pod size"] = value
        elif current_section == OVERSOUL:
            # oversoul data starts with "2 "
            oversoul[key[2:]] = value
        elif current_section == FIEND_ARENA:
            # fiend arena data starts with either "2 " or "3 "
            fiend_arena[key[2:]] = value
        elif current_section == FIEND_ARENA_OVERSOUL:
            # fiend arena oversoul data starts with "4 "
            fiend_arena_oversoul[key[2:]] = value
        else:
            # shared values (like immunities, etc) aren't prefixed
            shared[key] = value

    entry = BestiaryEntry()

    # combine shared data and normal/oversoul/fiend arena/fiend arena oversoul
    normal_data = get_data(data=normal, shared_data=shared)
    oversoul_data = get_data(data=oversoul, shared_data=shared)
    fiend_arena_data = get_data(data=fiend_arena, shared_data=shared)
    fiend_arena_oversoul_data = get_data(data=fiend_arena_oversoul, shared_data=shared)

    entry.name = name
    entry.via_infinito = parse_via_infinito_floors(normal_data["location"])

    populate_entry(entry, normal_data)
    populate_entry(entry.normal, normal_data)
    populate_entry(entry.normal.stats, normal_data)
    populate_entry(entry.normal.resistances, normal_data)

    entry.normal.drops = generate_loot_table(normal_data, "drop")
    entry.normal.steals = generate_loot_table(normal_data, "steal")
    entry.normal.bribes = generate_loot_table(normal_data, "bribe")

    if oversoul_data:
        oversoulable = BattleData()
        entry.oversoul = oversoulable
        populate_entry(oversoulable, oversoul_data)
        populate_entry(oversoulable.stats, oversoul_data)
        populate_entry(oversoulable.resistances, oversoul_data)

        oversoulable.drops = generate_loot_table(oversoul_data, "drop")
        oversoulable.steals = generate_loot_table(oversoul_data, "steal")
        oversoulable.bribes = generate_loot_table(oversoul_data, "bribe")

    if creature_creator:
        populate_entry(entry.creature_creator, creature_creator)

    if fiend_arena_data:
        arena = BattleData()
        entry.arena = arena
        populate_entry(arena, fiend_arena_data)
        populate_entry(arena.stats, fiend_arena_data)
        populate_entry(arena.resistances, fiend_arena_data)

        arena.drops = generate_loot_table(fiend_arena_data, "drop")
        arena.steals = generate_loot_table(fiend_arena_data, "steal")
        arena.bribes = generate_loot_table(fiend_arena_data, "bribe")

    if fiend_arena_oversoul_data:
        arena_oversoul = BattleData()
        entry.arena_oversoul = arena_oversoul
        populate_entry(arena_oversoul, fiend_arena_oversoul_data)
        populate_entry(arena_oversoul.stats, fiend_arena_oversoul_data)
        populate_entry(arena_oversoul.resistances, fiend_arena_oversoul_data)

        arena_oversoul.drops = generate_loot_table(fiend_arena_oversoul_data, "drop")
        arena_oversoul.steals = generate_loot_table(fiend_arena_oversoul_data, "steal")
        arena_oversoul.bribes = generate_loot_table(fiend_arena_oversoul_data, "bribe")

    populate_bribe_amount(entry)
    return entry


def populate_entry(entry, data):
    for wiki_key, (attribute, converter) in FIELDS.items():
        if wiki_key in data:
            setattr(entry, attribute, converter(data[wiki_key]))


def generate_loot_table(data: dict, prefix: str) -> LootTable | None:

    has_loot = f"common {prefix}" in data or f"rare {prefix}" in data
    if not has_loot:
        return

    table = LootTable()
    if f"common {prefix}" in data:
        table.common = parse_item(data[f"common {prefix}"])

    if f"rare {prefix}" in data:
        table.rare = parse_item(data[f"rare {prefix}"])

    if prefix == "steal" and "steal rate" in data:
        table.rate = parse_rate(data["steal rate"])

    if prefix == "drop" and "drop rate" in data:
        table.rate = parse_rate(data["drop rate"])

    return table


def populate_bribe_amount_for_battle_data(
    battle_data: BattleData | None, multiplier: float = 6.25
) -> None:
    if battle_data is None:
        return

    if (
        battle_data.bribes
        and (battle_data.bribes.common or battle_data.bribes.rare)
        and battle_data.stats.hp
    ):
        battle_data.bribes.rate = math.floor(battle_data.stats.hp * multiplier)


def populate_bribe_amount(entry: BestiaryEntry):
    populate_bribe_amount_for_battle_data(entry.normal)
    populate_bribe_amount_for_battle_data(entry.oversoul)
    populate_bribe_amount_for_battle_data(entry.arena)
    populate_bribe_amount_for_battle_data(entry.arena_oversoul)


from dataclasses import asdict


def battle_variant_map(entry, selector):
    return {
        "normal": selector(entry.normal),
        "oversoul": selector(entry.oversoul) if entry.oversoul else None,
        "fiendArena": (selector(entry.arena) if entry.arena else None),
        "fiendArenaOversoul": (
            selector(entry.arena_oversoul) if entry.arena_oversoul else None
        ),
    }


def battle_data_dict(battle_data):
    if battle_data is None:
        return None

    return asdict(battle_data)


def serialize_entry(entry: BestiaryEntry) -> dict:
    return {
        "bestiaryIndex": entry.bestiary_index,
        "name": entry.name,
        "species": entry.species,
        "oversoulAmount": entry.oversoul_amount,
        "chapters": entry.chapters,
        "locations": entry.locations,
        "viaInfinito": asdict(entry.via_infinito) if entry.via_infinito else None,
        "scanDescription": {
            "normal": entry.normal.scan_description,
            "oversoul": entry.oversoul.scan_description if entry.oversoul else None,
            "fiendArena": entry.arena.scan_description if entry.arena else None,
            "fiendArenaOversoul": (
                entry.arena_oversoul.scan_description if entry.arena_oversoul else None
            ),
        },
        "abilities": {
            "normal": entry.normal.abilities,
            "oversoul": entry.oversoul.abilities if entry.oversoul else None,
            "fiendArena": entry.arena.abilities if entry.arena else None,
            "fiendArenaOversoul": (
                entry.arena_oversoul.abilities if entry.arena_oversoul else None
            ),
        },
        "blueBullet": {
            "normal": entry.normal.blue_bullet,
            "oversoul": entry.oversoul.blue_bullet if entry.oversoul else None,
            "fiendArena": entry.arena.blue_bullet if entry.arena else None,
            "fiendArenaOversoul": (
                entry.arena_oversoul.blue_bullet if entry.arena_oversoul else None
            ),
        },
        "stats": {
            "normal": asdict(entry.normal.stats),
            "oversoul": asdict(entry.oversoul.stats) if entry.oversoul else None,
            "fiendArena": asdict(entry.arena.stats) if entry.arena else None,
            "fiendArenaOversoul": (
                asdict(entry.arena_oversoul.stats) if entry.arena_oversoul else None
            ),
        },
        "statusImmunities": {
            "normal": asdict(entry.normal.resistances),
            "oversoul": asdict(entry.oversoul.resistances) if entry.oversoul else None,
            "fiendArena": asdict(entry.arena.resistances) if entry.arena else None,
            "fiendArenaOversoul": (
                asdict(entry.arena_oversoul.resistances)
                if entry.arena_oversoul
                else None
            ),
        },
        "drops": {
            "normal": asdict(entry.normal.drops) if entry.normal.drops else None,
            "oversoul": (
                asdict(entry.oversoul.drops)
                if entry.oversoul and entry.oversoul.drops
                else None
            ),
            "fiendArena": (
                asdict(entry.arena.drops) if entry.arena and entry.arena.drops else None
            ),
            "fiendArenaOversoul": (
                asdict(entry.arena_oversoul.drops)
                if entry.arena_oversoul and entry.arena_oversoul.drops
                else None
            ),
        },
        "steals": {
            "normal": asdict(entry.normal.steals) if entry.normal.steals else None,
            "oversoul": (
                asdict(entry.oversoul.steals)
                if entry.oversoul and entry.oversoul.steals
                else None
            ),
            "fiendArena": (
                asdict(entry.arena.steals)
                if entry.arena and entry.arena.steals
                else None
            ),
            "fiendArenaOversoul": (
                asdict(entry.arena_oversoul.steals)
                if entry.arena_oversoul and entry.arena_oversoul.steals
                else None
            ),
        },
        "bribes": {
            "normal": asdict(entry.normal.bribes) if entry.normal.bribes else None,
            "oversoul": (
                asdict(entry.oversoul.bribes)
                if entry.oversoul and entry.oversoul.bribes
                else None
            ),
            "fiendArena": (
                asdict(entry.arena.bribes)
                if entry.arena and entry.arena.bribes
                else None
            ),
            "fiendArenaOversoul": (
                asdict(entry.arena_oversoul.bribes)
                if entry.arena_oversoul and entry.arena_oversoul.bribes
                else None
            ),
        },
        "creatureCreator": asdict(entry.creature_creator),
    }


def get_fiend_entry(name):
    for page_name in [name, f"{name}_(Final_Fantasy_X-2)"]:
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "titles": page_name,
            "format": "json",
        }

        response = requests.get(url, params=params)
        data = response.json()

        page = next(iter(data["query"]["pages"].values()))

        # Page doesn't exist
        if "missing" in page:
            continue

        wikitext = page["revisions"][0]["*"]

        code = mwparserfromhell.parse(wikitext)

        name = ""
        enemy_template = None

        for template in code.filter_templates():
            template_name = template.name.strip()

            if template_name == "infobox enemy":
                for param in template.params:
                    if param.name.strip() == "name":
                        name = clean_wikitext(str(param.value))
                        break

            elif template_name == "infobox enemy stats X2":
                enemy_template = template

            if name and enemy_template:
                break

        if enemy_template is not None:
            return build_entry(name, enemy_template.params)

    return None


entries = []

with open("bestiary.old.json") as json_data:
    fiend_data = json.load(json_data)

for fiend in fiend_data:
    name = fiend["name"].replace(" ", "_")

    entry = get_fiend_entry(name)

    if entry:
        entries.append(entry)
        print(f"{entry.name} loaded")
    else:
        print(f"Could not find: {name}")

serialized = [serialize_entry(entry) for entry in entries]

with open("bestiary_entries.json", "w", encoding="utf-8") as f:
    json.dump(serialized, f, indent=2, ensure_ascii=False)
