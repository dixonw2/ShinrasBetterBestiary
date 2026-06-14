using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace ShinrasBetterBestiary.Repositories;

public class UserBestiaryRepository : IUserBestiaryRepository
{
    private static readonly string UserDataDir =
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "ShinrasBetterBestiary");

    private static readonly string UserBestiaryPath = Path.Combine(UserDataDir, "bestiary.user.json");

    private static readonly JsonSerializerOptions JsonSerializerOptions = new()
        { PropertyNameCaseInsensitive = true, PropertyNamingPolicy = JsonNamingPolicy.CamelCase };

    public IReadOnlySet<int> LoadOversouledIds()
    {
        if (!File.Exists(UserBestiaryPath))
        {
            Directory.CreateDirectory(UserDataDir);

            File.WriteAllText(UserBestiaryPath, JsonSerializer.Serialize(
                new UserBestiarySave
                {
                    OversouledIds = []
                }, JsonSerializerOptions));
        }

        var json = File.ReadAllText(UserBestiaryPath);
        var savedEntries = JsonSerializer.Deserialize<UserBestiarySave>(json, JsonSerializerOptions);

        return savedEntries?.OversouledIds is null ? new HashSet<int>() : new HashSet<int>(savedEntries.OversouledIds);
    }

    public void SaveOversouled(IReadOnlySet<int> ids)
    {
        var json = JsonSerializer.Serialize(new UserBestiarySave { OversouledIds = ids.ToArray() },
            JsonSerializerOptions);
        File.WriteAllText(UserBestiaryPath, json);
    }
}

internal class UserBestiarySave
{
    public int[] OversouledIds { get; set; } = [];
}