package plugindungeon.api;

import org.bukkit.Location;

/**
 * Listener para interceptar a geração de salas do dungeon.
 */
public interface DungeonRoomGenerateListener {

    /**
     * Chamado quando uma sala está prestes a ser gerada.
     *
     * @param roomId   ID da sala.
     * @param location Local onde a sala será gerada.
     */
    void onRoomGenerate(String roomId, Location location);
}
