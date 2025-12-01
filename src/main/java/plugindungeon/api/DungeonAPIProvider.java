package plugindungeon.api;

public class DungeonAPIProvider {

    private static DungeonAPI api;

    public static void setAPI(DungeonAPI instance) {
        api = instance;
    }

    public static DungeonAPI getAPI() {
        if (api == null) {
            throw new IllegalStateException("DungeonAPI ainda não foi inicializada!");
        }
        return api;
    }

    public static boolean isAvailable() {
        return api != null;
    }
}
