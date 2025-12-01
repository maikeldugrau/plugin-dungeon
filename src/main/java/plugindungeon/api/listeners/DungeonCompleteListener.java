package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonCompleteListener {
    void onDungeonComplete(String dungeonId, Player player);
}
