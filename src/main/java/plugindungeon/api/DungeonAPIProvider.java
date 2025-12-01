package plugindungeon.api;

/**
 * Classe utilitária que fornece o acesso estático ao DungeonAPI.
 */
public final class DungeonAPIProvider {

    private static DungeonAPI api;

    private DungeonAPIProvider() {}

    /**
     * Registra a API para ser usada globalmente.
     *
     * @param dungeonAPI Instância da API.
     */
    public static void register(DungeonAPI dungeonAPI) {
        api = dungeonAPI;
    }

    /**
     * Obtém a API registrada.
     *
     * @return DungeonAPI registrada.
     */
    public static DungeonAPI get() {
        if (api == null) {
            throw new IllegalStateException("DungeonAPI não foi registrada ainda!");
        }
        return api;
    }
}
