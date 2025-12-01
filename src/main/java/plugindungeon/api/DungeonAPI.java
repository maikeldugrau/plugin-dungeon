package plugindungeon.api;

import org.bukkit.Location;
import org.bukkit.entity.Player;
import plugindungeon.api.listeners.*;
import plugindungeon.core.generation.RoomData;

import java.util.List;

public interface DungeonAPI {

    // LISTENERS
    void registerDungeonStartListener(DungeonStartListener listener);
    void registerDungeonCompleteListener(DungeonCompleteListener listener);
    void registerDungeonFailListener(DungeonFailListener listener);
    void registerDungeonLevelUpListener(DungeonLevelUpListener listener);

    void registerDungeonMobDeathListener(DungeonMobDeathListener listener);
    void registerDungeonBossDeathListener(DungeonBossDeathListener listener);
    void registerDungeonLootGenerateListener(DungeonLootGenerateListener listener);
    void registerDungeonRoomGenerateListener(DungeonRoomGenerateListener listener);

    void unregisterAllListeners(Object pluginInstance);

    boolean startDungeon(String dungeonId, String playerName);

    // DUNGEON MANAGER METHODS
    String generateDungeon(Location origin, int levels, int minRooms, intRooms, int maxRooms);

    List<RoomData> getActiveRooms(String dungeonId);

    void triggerNextRoom(String dungeonId);

    void teleportPlayerToDungeon(Player player, String dungeonId);
}
