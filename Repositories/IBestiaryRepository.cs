using System.Collections.Generic;
using ShinrasBetterBestiary.Models;

namespace ShinrasBetterBestiary.Repositories;

public interface IBestiaryRepository
{
    IReadOnlyList<FiendBestiaryEntryModel> Load();
}