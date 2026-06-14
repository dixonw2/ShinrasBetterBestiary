using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using CommunityToolkit.Mvvm.Input;
using ShinrasBetterBestiary.Models;
using ShinrasBetterBestiary.Repositories;

namespace ShinrasBetterBestiary.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    private readonly IBestiaryRepository _bestiaryRepository;
    private readonly IUserBestiaryRepository _userBestiaryRepository;

    // dummy constructor for previewer
    public MainWindowViewModel()
    {
        _bestiaryRepository = new BestiaryRepository();
        _userBestiaryRepository = new UserBestiaryRepository();
        BestiaryEntries = [];
    }

    public MainWindowViewModel(IBestiaryRepository bestiaryRepository, IUserBestiaryRepository userBestiaryRepository)
    {
        _bestiaryRepository = bestiaryRepository;
        _userBestiaryRepository = userBestiaryRepository;

        BestiaryEntries = GetUserBestiaryEntriesFromFile();
    }

    public int OversouledCount => BestiaryEntries.Count(x => x.Oversouled);
    public ObservableCollection<FiendBestiaryEntryModel> BestiaryEntries { get; private set; }

    [RelayCommand]
    private void ChangeTest()
    {
        var t = new Random();
        var ids = _userBestiaryRepository.LoadOversouledIds();

        var updatedIds = ids.Append(1 + t.Next(0, 131)).ToHashSet();

        foreach (var id in updatedIds)
        {
            var curFiend = BestiaryEntries.FirstOrDefault(x => x.BestiaryIndex == id && !x.Oversouled);
            if (curFiend != null)
            {
                curFiend.Oversouled = true;
            }
        }

        _userBestiaryRepository.SaveOversouled(updatedIds);
        BestiaryEntries = GetUserBestiaryEntriesFromFile();
    }

    [RelayCommand]
    private void ClearOversouled()
    {
        foreach (var fiend in BestiaryEntries)
        {
            fiend.Oversouled = false;
        }

        _userBestiaryRepository.SaveOversouled(new HashSet<int>());
    }

    private void Fiend_PropertyChanged(
        object? sender,
        PropertyChangedEventArgs e)
    {
        if (e.PropertyName != nameof(FiendBestiaryEntryModel.Oversouled))
        {
            return;
        }

        OnPropertyChanged(nameof(OversouledCount));

        _userBestiaryRepository.SaveOversouled(
            BestiaryEntries.Where(x => x.Oversouled)
                .Select(x => x.BestiaryIndex).ToHashSet());
    }

    private ObservableCollection<FiendBestiaryEntryModel> GetUserBestiaryEntriesFromFile()
    {
        var bestiary = _bestiaryRepository.Load();
        var oversouledIds = _userBestiaryRepository.LoadOversouledIds();

        foreach (var fiend in bestiary)
        {
            fiend.Oversouled = oversouledIds.Contains(fiend.BestiaryIndex);

            fiend.PropertyChanged += Fiend_PropertyChanged;
        }

        return new ObservableCollection<FiendBestiaryEntryModel>(bestiary);
    }
}