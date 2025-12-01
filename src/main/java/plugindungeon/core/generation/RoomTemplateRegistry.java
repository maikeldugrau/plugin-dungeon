package plugindungeon.core.generation;

import plugindungeon.DungeonPlugin;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class RoomTemplateRegistry {

    private final JavaPlugin plugin;
    private final Map<String, File> schematicFiles = new ConcurrentHashMap<>();
    private final Set<RoomType> schematicRooms = EnumSet.of(RoomType.START, RoomType.MINIBOSS, RoomType.BOSS, RoomType.TREASURE);

    public RoomTemplateRegistry(JavaPlugin plugin) {
        this.plugin = plugin;
        loadSchematicsFolder();
    }

    private void loadSchematicsFolder() {
        File dir = new File(plugin.getDataFolder(), "schematics");
        if (!dir.exists()) dir.mkdirs();

        File[] files = dir.listFiles((d, name) -> name.endsWith(".schem") || name.endsWith(".schematic") || name.endsWith(".nbt"));
        if (files == null) return;
        for (File f : files) schematicFiles.put(f.getName(), f);
        plugin.getLogger().info("Loaded schematics: " + schematicFiles.size());
    }

    public boolean isSchematicRoom(RoomType type) { return schematicRooms.contains(type); }
    public Optional<File> getRandomSchematic() {
        if (schematicFiles.isEmpty()) return Optional.empty();
        List<File> list = new ArrayList<>(schematicFiles.values());
        return Optional.of(list.get(new Random().nextInt(list.size())));
    }
    public Optional<File> getSchematicByName(String name) { return Optional.ofNullable(schematicFiles.get(name)); }
}
