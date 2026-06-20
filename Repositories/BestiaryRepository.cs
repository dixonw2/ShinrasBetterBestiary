using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Avalonia.Platform;

namespace ShinrasBetterBestiary.Repositories;

public class BestiaryRepository : IBestiaryRepository
{
    private static readonly JsonSerializerOptions JsonSerializerOptions = new() { PropertyNameCaseInsensitive = true };

    public IReadOnlyList<FiendModel> Load()
    {
        var uri = new Uri($"avares://{nameof(ShinrasBetterBestiary)}/Assets/Data/bestiary.json");

        using var stream = AssetLoader.Open(uri);
        using var reader = new StreamReader(stream);
        var json = reader.ReadToEnd();

        var jsonEntries = JsonSerializer.Deserialize<List<FiendModel>>(json, JsonSerializerOptions);

        IReadOnlyList<FiendModel> entries = new List<FiendModel>(jsonEntries ?? []);
        return entries;
    }
}