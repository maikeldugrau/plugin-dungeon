package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonBossDeathListener {
    void onDungeonBossDeath(String dungeonId, Player killer);
}
