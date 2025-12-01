package plugindungeon.loot;

import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.block.Chest;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.Random;

public class ChestLootManager {

    private final JavaPlugin plugin;
    private final Random r = new Random();

    public ChestLootManager(JavaPlugin plugin) { this.plugin = plugin; }

    public void fillChestsInRoom(Location origin, int width, int height, int depth, int level) {
        for (int x = origin.getBlockX(); x < origin.getBlockX() + width; x++) {
            for (int y = origin.getBlockY(); y < origin.getBlockY() + height; y++) {
                for (int z = origin.getBlockZ(); z < origin.getBlockZ() + depth; z++) {
                    if (origin.getWorld().getBlockAt(x,y,z).getType() == Material.CHEST) {
                        Chest chest = (Chest) origin.getWorld().getBlockAt(x,y,z).getState();
                        chest.getBlockInventory().addItem(getLoot(level));
                    }
                }
            }
        }
    }

    private ItemStack getLoot(int level) {
        return switch (r.nextInt(3)) {
            case 0 -> new ItemStack(Material.GOLD_INGOT, 4 + level);
            case 1 -> new ItemStack(Material.IRON_INGOT, 6 + level);
            default -> new ItemStack(Material.DIAMOND, Math.max(1, level/2));
        };
    }
}

