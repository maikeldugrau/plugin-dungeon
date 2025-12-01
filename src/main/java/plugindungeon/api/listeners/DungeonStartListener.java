package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonStartListener {
    void onDungeonStart(String dungeonId, Player player);
}
