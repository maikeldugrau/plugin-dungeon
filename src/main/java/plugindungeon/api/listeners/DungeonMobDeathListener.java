package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonMobDeathListener {
    void onDungeonMobDeath(String dungeonId, Player killer);
}
