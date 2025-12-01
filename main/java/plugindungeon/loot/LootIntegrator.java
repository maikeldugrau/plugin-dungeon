package plugindungeon.loot;

import org.bukkit.entity.LivingEntity;
import org.bukkit.plugin.java.JavaPlugin;

public class LootIntegrator {

    private final JavaPlugin plugin;

    public LootIntegrator(JavaPlugin plugin) { this.plugin = plugin; }

    public void dropBossLoot(LivingEntity boss, int level) {
        // placeholder: drop diamonds and nether star
        boss.getWorld().dropItemNaturally(boss.getLocation(), new org.bukkit.inventory.ItemStack(org.bukkit.Material.DIAMOND, 3 + level));
        boss.getWorld().dropItemNaturally(boss.getLocation(), new org.bukkit.inventory.ItemStack(org.bukkit.Material.NETHER_STAR, 1));
    }
}

