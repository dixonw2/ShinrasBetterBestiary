using System.Collections.Generic;

namespace ShinrasBetterBestiary.Repositories;

public interface IUserBestiaryRepository
{
    IReadOnlySet<int> LoadOversouledIds();
    void SaveOversouled(IReadOnlySet<int> ids);
}