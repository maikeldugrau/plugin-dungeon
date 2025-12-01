package plugindungeon.api;

public class DungeonAPIProvider {
    private static DungeonAPI api;
    public static void setAPI(DungeonAPI instance) { api = instance; }
    public static DungeonAPI get() { return api; }
}
