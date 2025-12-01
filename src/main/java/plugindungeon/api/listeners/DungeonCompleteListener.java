package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonCompleteListener {
    void onDungeonComplete(Player player, String dungeonId);
}
