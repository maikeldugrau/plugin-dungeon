package plugindungeon.api;

public final class DungeonAPIProvider {
    private static DungeonAPI apiInstance;
    private DungeonAPIProvider(){}

    public static void set(DungeonAPI api) { apiInstance = api; }
    public static void setAPI(DungeonAPI api) { set(api); }

    public static DungeonAPI get() {
        if (apiInstance == null) throw new IllegalStateException("DungeonAPI not registered");
        return apiInstance;
    }

    public static boolean isAvailable() { return apiInstance != null; }
}
