package plugindungeon.api;

import org.bukkit.Location;
import org.bukkit.entity.Player;
import plugindungeon.api.listeners.*;
import plugindungeon.core.generation.RoomData;

import java.util.List;

/**
 * API pública do plugin — versão "completa" que expõe métodos de gerenciamento e listeners.
 */
public interface DungeonAPI {

    // ===== Listeners =====
    void registerDungeonStartListener(DungeonStartListener listener);
    void registerDungeonCompleteListener(DungeonCompleteListener listener);
    void registerDungeonFailListener(DungeonFailListener listener);
    void registerDungeonLevelUpListener(DungeonLevelUpListener listener);

    void registerDungeonMobDeathListener(DungeonMobDeathListener listener);
    void registerDungeonBossDeathListener(DungeonBossDeathListener listener);
    void registerDungeonLootGenerateListener(DungeonLootGenerateListener listener);
    void registerDungeonRoomGenerateListener(DungeonRoomGenerateListener listener);

    void unregisterAllListeners(Object pluginInstance);

    // ===== Control =====
    boolean startDungeon(String dungeonId, String playerName);

    // ===== Dungeon management (necessário para comandos/geração) =====
    /**
     * Gera uma dungeon no local informado. Retorna o ID da dungeon gerada.
     */
    String generateDungeon(Location origin, int levels, int minRooms, int maxRooms);

    /**
     * Retorna lista de rooms ativas (RoomData) de uma dungeon.
     */
    List<RoomData> getActiveRooms(String dungeonId);

    /**
     * Força o disparo para a próxima sala/progresso da dungeon.
     */
    void triggerNextRoom(String dungeonId);

    /**
     * Teleporta jogador para a dungeon (usado por comandos/admin).
     */
    void teleportPlayerToDungeon(Player player, String dungeonId);

    /**
     * Fecha/limpa todos os dungeons (shutdown).
     */
    void shutdownAll();
}
