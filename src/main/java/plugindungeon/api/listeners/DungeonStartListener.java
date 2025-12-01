package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonStartListener {
    void onDungeonStart(Player player, String dungeonId);
}
