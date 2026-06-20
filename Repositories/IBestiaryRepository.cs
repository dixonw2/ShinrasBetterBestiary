using System.Collections.Generic;

namespace ShinrasBetterBestiary.Repositories;

public interface IBestiaryRepository
{
    IReadOnlyList<FiendModel> Load();
}