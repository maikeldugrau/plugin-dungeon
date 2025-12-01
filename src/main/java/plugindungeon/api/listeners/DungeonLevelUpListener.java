package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonLevelUpListener {
    void onDungeonLevelUp(Player player, String dungeonId, int newLevel);
}
