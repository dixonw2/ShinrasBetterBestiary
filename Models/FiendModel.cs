using System.Collections.Generic;
using CommunityToolkit.Mvvm.ComponentModel;

public partial class FiendModel : ObservableObject
{
    [ObservableProperty] private bool captured;
    [ObservableProperty] private bool oversouled;

    public int BestiaryIndex { get; init; }
    public string Name { get; init; } = "";
    public string Species { get; init; } = "";
    public int OversoulAmount { get; init; }

    public List<int> Chapters { get; init; } = [];
    public List<string> Locations { get; init; } = [];

    public ViaInfinitoRange? ViaInfinito { get; init; }

    public Variant<string>? ScanDescription { get; init; } = new();
    public Variant<List<string>>? Abilities { get; init; } = new();
    public Variant<List<string>>? BlueBullet { get; init; } = new();

    public Variant<BattleStats>? Stats { get; init; } = new();
    public Variant<StatusImmunities>? StatusImmunities { get; init; } = new();

    public Variant<ItemTable>? Drops { get; init; } = new();
    public Variant<ItemTable>? Steals { get; init; } = new();
    public Variant<ItemTable>? Bribes { get; init; } = new();

    public CreatureCreatorData? CreatureCreator { get; init; }
}

public class Variant<T>
{
    public T? Normal { get; init; }
    public T? Oversoul { get; init; }
    public T? FiendArena { get; init; }
    public T? FiendArenaOversoul { get; init; }
}

public class ViaInfinitoRange
{
    public int Min { get; init; }
    public int Max { get; init; }
}

public class BattleStats
{
    public int Level { get; init; }
    public int Hp { get; init; }
    public int Mp { get; init; }
    public int Strength { get; init; }
    public int Magic { get; init; }
    public int Defense { get; init; }
    public int MagicDefense { get; init; }
    public int Agility { get; init; }
    public int Accuracy { get; init; }
    public int Evasion { get; init; }
    public int Luck { get; init; }
    public int Exp { get; init; }
    public int Ap { get; init; }
    public int Gil { get; init; }
    public int PilferGil { get; init; }
    public int Zantetsu { get; init; }
    public EjectData? Eject { get; init; }
}

public class EjectData
{
    public bool Immune { get; init; }
    public int? Chance { get; init; }
}

public class DeathData
{
    public bool Immune { get; init; }
    public int? Chance { get; init; }
}

public class StatusImmunities
{
    public int Fire { get; init; }
    public int Ice { get; init; }
    public int Lightning { get; init; }
    public int Water { get; init; }
    public int Holy { get; init; }

    public bool Gravity { get; init; }
    public bool Silence { get; init; }
    public bool Sleep { get; init; }
    public bool Darkness { get; init; }
    public bool Poison { get; init; }
    public bool Confusion { get; init; }
    public bool Berserk { get; init; }
    public bool Curse { get; init; }
    public bool Petrification { get; init; }
    public bool Slow { get; init; }
    public bool Delay { get; init; }
    public bool Stop { get; init; }

    public bool ActionCancel { get; init; }

    public bool MultiAttack { get; init; }

    public bool StrengthDown { get; init; }

    public bool MagicDown { get; init; }

    public bool DefenseDown { get; init; }

    public bool MagicDefenseDown { get; init; }

    public bool LuckDown { get; init; }

    public bool AccuracyDown { get; init; }

    public bool EvasionDown { get; init; }

    public DeathData Death { get; init; }
    public bool Doom { get; init; }

    public bool FractDamage { get; init; }

    public bool Reflect { get; init; }
    public bool Physical { get; init; }
    public bool Magical { get; init; }
}

public class ItemTable
{
    public ItemDrop? Common { get; init; }
    public ItemDrop? Rare { get; init; }
    public double Rate { get; init; }
}

public class ItemDrop
{
    public string Item { get; init; } = "";
    public int Quantity { get; init; }
}

public class CreatureCreatorData
{
    public int? BestiaryIndex { get; init; }

    public string? PodSize { get; init; }

    public string? Clear { get; init; }

    public List<string> Locations { get; init; } = [];
    public List<int> Chapters { get; init; } = [];
    public List<string> Teams { get; init; } = [];
}