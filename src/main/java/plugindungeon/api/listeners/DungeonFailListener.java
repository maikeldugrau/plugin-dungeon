package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonFailListener {
    void onDungeonFail(Player player, String dungeonId);
}
