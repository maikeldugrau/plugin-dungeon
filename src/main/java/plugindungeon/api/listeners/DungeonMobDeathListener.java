package plugindungeon.api.listeners;

import org.bukkit.entity.Player;
import org.bukkit.entity.LivingEntity;

public interface DungeonMobDeathListener {
    void onMobDeath(Player player, LivingEntity mob, String dungeonId, int floor);
}
