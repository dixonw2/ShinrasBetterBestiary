using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using ShinrasBetterBestiary.Repositories;

namespace ShinrasBetterBestiary.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    /*
     * Elder Drake:    Can appear as an on-map encounter floors 1-99
     * Tonberry:       Can appear as an on-map encounter floors 1-99
     * Mega Tonberry:  Can appear as an on-map encounter floors 41-99, regular 61-99
     * Georapella:     Can appear only in the Bevelle Underground
     * Precepts Guard: Can appear only in the Bevelle Underground
     */
    private static readonly HashSet<string> SpecialFiends =
        ["Elder Drake", "Tonberry", "Mega Tonberry", "Georapella", "Precepts Guard"];

    private readonly IBestiaryRepository _bestiaryRepository;
    private readonly IUserBestiaryRepository _userBestiaryRepository;
    private bool _bulkUpdating;

    [ObservableProperty] private int _oversouledCount;
    [ObservableProperty] private string _viaInfinitoText = string.Empty;

    public MainWindowViewModel(IBestiaryRepository? bestiaryRepository = null,
        IUserBestiaryRepository? userBestiaryRepository = null)
    {
        _bestiaryRepository = bestiaryRepository ?? new BestiaryRepository();
        _userBestiaryRepository = userBestiaryRepository ?? new UserBestiaryRepository();

        BestiaryEntries = GetUserBestiaryEntriesFromFile();
        RefreshProperties();
    }

    public ObservableCollection<FiendModel> BestiaryEntries { get; private set; }

    private void Fiend_PropertyChanged(
        object? sender,
        PropertyChangedEventArgs e)
    {
        // if bulkUpdating set, don't notify of property change (prevents freezes on reset)
        if (e.PropertyName != nameof(FiendModel.Oversouled) || _bulkUpdating)
        {
            return;
        }

        RefreshProperties();

        _userBestiaryRepository.SaveOversouled(
            BestiaryEntries.Where(x => x.Oversouled)
                .Select(x => x.BestiaryIndex).ToHashSet());
    }

    private string GetViaInfinitoFloors()
    {
        // select fiends not oversouled
        var floors = BestiaryEntries
            .Where(x => !x.Oversouled)
            .ToList();

        // check if fiends not oversouled are special cases
        var specialFloor = floors.Any(x => SpecialFiends.Contains(x.Name));

        var sortedFloors = floors
            .Where(x => !SpecialFiends.Contains(x.Name))
            .Where(x => x.ViaInfinito is not null)
            .Select(x => (x.ViaInfinito!.Min, x.ViaInfinito!.Max))
            .Distinct()
            .OrderBy(x => x.Min)
            .ToList();

        if (sortedFloors.Count == 0)
        {
            return specialFloor
                ? "Via Infinito Floors: Check special fiends"
                : string.Empty;
        }

        List<(int Min, int Max)> merged = [];

        var curMin = sortedFloors[0].Min;
        var curMax = sortedFloors[0].Max;

        // skip first as that is already curMin and curMax
        foreach (var floor in sortedFloors.Skip(1))
        {
            if (floor.Min <= curMax + 1)
            {
                curMax = Math.Max(curMax, floor.Max);
            }
            else
            {
                merged.Add((curMin, curMax));

                curMin = floor.Min;
                curMax = floor.Max;
            }
        }

        merged.Add((curMin, curMax));
        var viaInfinitoFloors = "Via Infinito: ";
        // perform x.Min == x.Max check for Paragon, who only shows up on floor 100
        viaInfinitoFloors += string.Join(", ", merged.Select(x =>
            x.Min == x.Max ? x.Min.ToString() : $"{x.Min}-{x.Max}"));
        if (specialFloor)
        {
            viaInfinitoFloors += " (Check special fiends)";
        }

        return viaInfinitoFloors;
    }

    private ObservableCollection<FiendModel> GetUserBestiaryEntriesFromFile()
    {
        var bestiary = _bestiaryRepository.Load();
        var oversouledIds = _userBestiaryRepository.LoadOversouledIds();

        foreach (var fiend in bestiary)
        {
            fiend.Oversouled = oversouledIds.Contains(fiend.BestiaryIndex);
            fiend.PropertyChanged += Fiend_PropertyChanged;
        }

        return new ObservableCollection<FiendModel>(bestiary);
    }

    private void RefreshProperties()
    {
        OversouledCount = BestiaryEntries.Count(x => x.Oversouled);
        ViaInfinitoText = GetViaInfinitoFloors();
    }

    #region Commands

    [RelayCommand]
    private void ChangeTest()
    {
        var t = new Random();
        var ids = _userBestiaryRepository.LoadOversouledIds();

        var updatedIds = ids.Append(1 + t.Next(0, 131)).ToHashSet();

        var lookup = BestiaryEntries.ToDictionary(x => x.BestiaryIndex);

        foreach (var id in updatedIds)
        {
            if (lookup.TryGetValue(id, out var fiend) && !fiend.Oversouled)
            {
                fiend.Oversouled = true;
            }
        }

        _userBestiaryRepository.SaveOversouled(updatedIds);
        BestiaryEntries = GetUserBestiaryEntriesFromFile();
    }

    [RelayCommand]
    private void ClearOversouled()
    {
        _bulkUpdating = true;

        foreach (var fiend in BestiaryEntries)
        {
            fiend.Oversouled = false;
        }

        _bulkUpdating = false;

        RefreshProperties();

        _userBestiaryRepository.SaveOversouled(new HashSet<int>());
    }

    #endregion
}