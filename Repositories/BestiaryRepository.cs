using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Avalonia.Platform;
using ShinrasBetterBestiary.Models;

namespace ShinrasBetterBestiary.Repositories;

public class BestiaryRepository : IBestiaryRepository
{
    private static readonly JsonSerializerOptions JsonSerializerOptions = new() { PropertyNameCaseInsensitive = true };

    public IReadOnlyList<FiendBestiaryEntryModel> Load()
    {
        var uri = new Uri("avares://ShinrasBetterBestiary/Assets/Data/bestiary.json");

        using var stream = AssetLoader.Open(uri);
        using var reader = new StreamReader(stream);
        var json = reader.ReadToEnd();

        var jsonEntries = JsonSerializer.Deserialize<List<FiendBestiaryEntryModel>>(json, JsonSerializerOptions);

        IReadOnlyList<FiendBestiaryEntryModel> entries = new List<FiendBestiaryEntryModel>(jsonEntries ?? []);
        return entries;
    }
}