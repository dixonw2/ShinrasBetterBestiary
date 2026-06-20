from dataclasses import dataclass, field


@dataclass
class ItemDrop:
    item: str | None = None
    quantity: int | None = None


@dataclass
class LootTable:
    common: ItemDrop | None = None
    rare: ItemDrop | None = None
    rate: float = 1


@dataclass
class ViaInfinito:
    min: int | None = None
    max: int | None = None


@dataclass
class Stats:
    level: int | None = None
    hp: int | None = None
    mp: int | None = None

    strength: int | None = None
    magic: int | None = None
    defense: int | None = None
    magic_defense: int | None = None

    agility: int | None = None
    accuracy: int | None = None
    evasion: int | None = None
    luck: int | None = None

    exp: int | None = None
    ap: int | None = None
    gil: int | None = None
    pilfer_gil: int | None = None

    zantetsu: int | None = None
    eject: int | bool | None = None


@dataclass
class Resistances:
    # -1: absorb
    # 0: immune
    # 1: neutral
    # 2: weak
    fire: int = 1
    ice: int = 1
    lightning: int = 1
    water: int = 1
    holy: int = 1

    # gravity damage is either immune or not, not weak
    gravity: bool = False

    silence: bool = False
    sleep: bool = False
    darkness: bool = False
    poison: bool = False
    confusion: bool = False
    berserk: bool = False
    curse: bool = False
    petrification: bool = False
    slow: bool = False
    delay: bool = False
    stop: bool = False
    action_cancel: bool = False
    multi_attack: bool = False
    str_down: bool = False
    mag_down: bool = False
    def_down: bool = False
    mag_def_down: bool = False
    luck_down: bool = False
    accu_down: bool = False
    eva_down: bool = False

    death: int | bool = False
    doom: bool = False
    fract_damage: bool = False
    reflect: bool = False
    physical: bool = False
    magical: bool = (
        False  # nothing is immune to magic; 255 magic defense will show immune though (Cactuar)
    )


@dataclass
class BattleData:
    stats: Stats = field(default_factory=Stats)
    resistances: Resistances = field(default_factory=Resistances)
    blue_bullet: list[str] = field(default_factory=list)

    drops: LootTable | None = None
    steals: LootTable | None = None
    bribes: LootTable | None = None

    scan_description: str | None = None
    abilities: list[str] = field(default_factory=list)


@dataclass
class CreatureCreator:
    bestiary_index: int | None = None
    pod_size: str | None = None
    clear: str | None = None
    locations: list[str] = field(default_factory=list)
    chapters: list[int] = field(default_factory=list)
    teams: list[str] = field(default_factory=list)


@dataclass
class BestiaryEntry:
    bestiary_index: int | None = None
    name: str | None = None
    species: str | None = None
    oversoul_amount: int | None = None

    chapters: list[int] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)

    via_infinito: ViaInfinito | None = field(default_factory=ViaInfinito)

    normal: BattleData = field(default_factory=BattleData)
    oversoul: BattleData | None = None
    arena: BattleData | None = None
    arena_oversoul: BattleData | None = None

    creature_creator: CreatureCreator = field(default_factory=CreatureCreator)
