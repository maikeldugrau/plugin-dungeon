package plugindungeon.api.listeners;

import org.bukkit.entity.Player;
import org.bukkit.entity.LivingEntity;

public interface DungeonBossDeathListener {
    void onBossDeath(Player player, LivingEntity boss, String dungeonId, int floor);
}
