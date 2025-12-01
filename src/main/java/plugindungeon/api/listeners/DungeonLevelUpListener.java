package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonLevelUpListener {
    void onDungeonLevelUp(String dungeonId, Player player, int newLevel);
}
