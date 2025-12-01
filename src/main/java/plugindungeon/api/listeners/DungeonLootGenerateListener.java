package plugindungeon.api.listeners;

import org.bukkit.entity.Player;

public interface DungeonLootGenerateListener {
    void onDungeonLootGenerate(String dungeonId, Player player);
}
