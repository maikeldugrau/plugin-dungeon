package plugindungeon.api;

import org.bukkit.Location;
import org.bukkit.entity.Player;
import java.util.List;
import plugindungeon.core.generation.RoomData;

public interface DungeonAPI {
    String generateDungeon(Location origin, int levels, int minRooms, int maxRooms);
    void registerDungeonCompleteListener(DungeonCompleteListener listener);
    List<RoomData> getActiveRooms(String dungeonId);
    void triggerNextRoom(String dungeonId);
    void teleportPlayerToDungeon(Player player, String dungeonId);
}
