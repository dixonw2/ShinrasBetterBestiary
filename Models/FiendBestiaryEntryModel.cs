using CommunityToolkit.Mvvm.ComponentModel;

namespace ShinrasBetterBestiary.Models;

public partial class FiendBestiaryEntryModel : ObservableObject
{
    public int Page { get; }
    public int BestiaryIndex { get; }
    public int EncounterIndex { get; }
    public string Name { get; }
    public int Chapter { get; }
    public string Location { get; }
    public int ViaInfinitoFloorMin { get; }
    public int ViaInfinitoFloorMax { get; }
    public string Comment { get; }
    public string BlueBullet { get; }

    [ObservableProperty]
    private bool oversouled;

    public FiendBestiaryEntryModel(
        int page,
        int bestiaryIndex,
        int encounterIndex,
        string name,
        int chapter,
        string location,
        int viaInfinitoFloorMin,
        int viaInfinitoFloorMax,
        string comment,
        string blueBullet,
        bool oversouled = false)
    {
        Page = page;
        BestiaryIndex = bestiaryIndex;
        EncounterIndex = encounterIndex;
        Name = name;
        Chapter = chapter;
        Location = location;
        ViaInfinitoFloorMin = viaInfinitoFloorMin;
        ViaInfinitoFloorMax = viaInfinitoFloorMax;
        Comment = comment;
        BlueBullet = blueBullet;

        this.oversouled = oversouled;
    }
}