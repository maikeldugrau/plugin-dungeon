package plugindungeon.api.listeners;

import org.bukkit.inventory.ItemStack;

import java.util.List;

public interface DungeonLootGenerateListener {
    void onLootGenerated(List<ItemStack> loot, String dungeonId, int floor, boolean isBoss);
}
