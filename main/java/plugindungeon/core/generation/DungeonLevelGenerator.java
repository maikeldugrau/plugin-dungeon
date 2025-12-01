package plugindungeon.core.generation;

import plugindungeon.DungeonPlugin;
import org.bukkit.Location;

import java.util.Random;
import java.util.UUID;

public class DungeonLevelGenerator {

    private final DungeonPlugin plugin;
    private final RoomGenerator roomGenerator;
    private final RoomTemplateRegistry registry;
    private final Random random = new Random();

    public DungeonLevelGenerator(DungeonPlugin plugin, RoomGenerator roomGenerator, RoomTemplateRegistry registry) {
        this.plugin = plugin;
        this.roomGenerator = roomGenerator;
        this.registry = registry;
    }

    public String generateLevel(Location start, int minRooms, int maxRooms, RoomTheme theme, int levelIndex) {
        int rooms = Math.max(3, random.nextInt(maxRooms - minRooms + 1) + minRooms);
        Location cursor = start.clone();
        int spacing = plugin.getConfig().getInt("dungeon.roomSpacing", 40);

        // start room
        RoomData startRoom = new RoomData(UUID.randomUUID().toString(), RoomType.START, RoomTheme.NONE, cursor.clone(), 16, 8, 16);
        roomGenerator.generateRoom(startRoom);
        cursor.add(spacing, 0, 0);

        for (int i = 1; i < rooms - 1; i++) {
            RoomType t = pickRoomType();
            RoomTheme th = random.nextDouble() < 0.8 ? theme : RoomTheme.NONE;
            RoomData r = new RoomData(UUID.randomUUID().toString(), t, th, cursor.clone(), 16 + random.nextInt(10), 8 + random.nextInt(4), 16 + random.nextInt(10));
            roomGenerator.generateRoom(r);
            cursor.add(spacing, 0, 0);
        }

        // miniboss
        RoomData minb = new RoomData(UUID.randomUUID().toString(), RoomType.MINIBOSS, theme, cursor.clone(), 24, 10, 24);
        roomGenerator.generateRoom(minb);
        cursor.add(spacing,0,0);

        // boss
        RoomData boss = new RoomData(UUID.randomUUID().toString(), RoomType.BOSS, theme, cursor.clone(), 40, 16, 40);
        roomGenerator.generateRoom(boss);

        return "level-" + levelIndex;
    }

    private RoomType pickRoomType() {
        int r = random.nextInt(100);
        if (r < 10) return RoomType.TRAP;
        if (r < 40) return RoomType.PLATFORM;
        return RoomType.STANDARD;
    }
}

