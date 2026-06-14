using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using ShinrasBetterBestiary.Repositories;
using ShinrasBetterBestiary.ViewModels;
using ShinrasBetterBestiary.Views;

namespace ShinrasBetterBestiary;

public class App : Application
{
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            IBestiaryRepository bestRepo = new BestiaryRepository();
            IUserBestiaryRepository userRepo = new UserBestiaryRepository();

            desktop.MainWindow = new MainWindow
            {
                DataContext = new MainWindowViewModel(bestRepo, userRepo)
            };
        }

        base.OnFrameworkInitializationCompleted();
    }
}