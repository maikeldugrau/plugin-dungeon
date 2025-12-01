package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonFailListener {
    void onDungeonFail(String dungeonId, Player player);
}
