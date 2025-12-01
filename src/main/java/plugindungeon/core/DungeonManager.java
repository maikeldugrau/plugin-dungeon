package plugindungeon.core;

import plugindungeon.DungeonPlugin;
import plugindungeon.api.DungeonAPI;
import plugindungeon.api.DungeonAPIProvider;
import plugindungeon.core.generation.DungeonRoomGenerator;
import plugindungeon.core.generation.RoomData;
import plugindungeon.loot.LootIntegrator;
import plugindungeon.mobs.LordeCataclismo;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Player;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class DungeonManager implements DungeonAPI {

    private final DungeonPlugin plugin;
    private final DungeonRoomGenerator generator;
    private final Map<String, List<RoomData>> activeDungeons = new ConcurrentHashMap<>();
    private final LootIntegrator lootIntegrator;

    public DungeonManager(DungeonPlugin plugin, DungeonRoomGenerator generator) {
        this.plugin = plugin;
        this.generator = generator;
        this.lootIntegrator = new LootIntegrator(plugin);
    }

    @Override
    public String generateDungeon(Location origin, int levels, int minRooms, int maxRooms) {
        String id = generator.generateDungeon(origin, levels, minRooms, maxRooms);
        // For now store empty list (RoomData objects are created inside generator — for fuller integration generator should return them)
        activeDungeons.put(id, new ArrayList<>());
        plugin.getLogger().info("Dungeon generated id=" + id + " at " + origin);
        return id;
    }

    @Override
    public void registerDungeonCompleteListener(DungeonCompleteListener listener) {
        // simple placeholder - not storing listeners in this simplified manager
    }

    @Override
    public List<RoomData> getActiveRooms(String dungeonId) {
        return activeDungeons.getOrDefault(dungeonId, Collections.emptyList());
    }

    @Override
    public void triggerNextRoom(String dungeonId) {
        plugin.getLogger().info("Trigger next room for " + dungeonId);
    }

    @Override
    public void teleportPlayerToDungeon(Player player, String dungeonId) {
        // crude: teleport to world spawn or first known room center
        List<RoomData> rooms = getActiveRooms(dungeonId);
        if (!rooms.isEmpty()) player.teleport(rooms.get(0).getCenter());
        else player.teleport(Bukkit.getWorlds().get(0).getSpawnLocation());
    }

    // convenience for admin preview of boss
    public void forceSpawnBossPreview(Location at) {
        LordeCataclismo boss = new LordeCataclismo(plugin, lootIntegrator, 1);
        boss.spawn(at.add(0,2,0));
    }

    public void shutdownAll() {
        // TODO: clean up active dungeons, boss tasks, etc.
    }

    public interface DungeonCompleteListener {
        void onDungeonComplete(String dungeonId, Player player);
    }
}
