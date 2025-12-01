package plugindungeon.api;

/**
 * Listener chamado quando um jogador completa um dungeon.
 */
public interface DungeonCompleteListener {

    /**
     * Executado quando o dungeon é completado.
     *
     * @param playerName Nome do jogador que completou.
     * @param dungeonId  ID do dungeon completado.
     */
    void onDungeonComplete(String playerName, String dungeonId);
}
