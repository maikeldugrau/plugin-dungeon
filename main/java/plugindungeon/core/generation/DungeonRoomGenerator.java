package plugindungeon.core.generation;

import plugindungeon.DungeonPlugin;
import org.bukkit.Location;

public class DungeonRoomGenerator {

    private final DungeonPlugin plugin;
    private final RoomTemplateRegistry registry;
    private final RoomGenerator roomGenerator;
    private final DungeonLevelGenerator levelGenerator;

    public DungeonRoomGenerator(DungeonPlugin plugin) {
        this.plugin = plugin;
        this.registry = plugin.getTemplateRegistry();
        this.roomGenerator = new RoomGenerator(plugin, registry, plugin.getSchematicPaster());
        this.levelGenerator = new DungeonLevelGenerator(plugin, roomGenerator, registry);
    }

    public String generateDungeon(Location start, int levels, int minRooms, int maxRooms) {
        // naive multi-level generation
        for (int i = 0; i < levels; i++) {
            RoomTheme theme = RoomTheme.values()[i % RoomTheme.values().length];
            Location levelStart = start.clone().add(0, i * 70, 0);
            levelGenerator.generateLevel(levelStart, minRooms, maxRooms, theme, i+1);
        }
        return java.util.UUID.randomUUID().toString();
    }
}

