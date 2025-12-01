package plugindungeon.core.generation;

import plugindungeon.DungeonPlugin;
import plugindungeon.world.AsyncSchematicPaster;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;

import java.io.File;
import java.util.Random;

public class RoomGenerator {

    private final DungeonPlugin plugin;
    private final RoomTemplateRegistry registry;
    private final AsyncSchematicPaster paster;
    private final Random random = new Random();

    public RoomGenerator(DungeonPlugin plugin, RoomTemplateRegistry registry, AsyncSchematicPaster paster) {
        this.plugin = plugin;
        this.registry = registry;
        this.paster = paster;
    }

    public void generateRoom(RoomData roomData) {
        if (registry.isSchematicRoom(roomData.type)) {
            registry.getRandomSchematic().ifPresent(file -> paster.pasteWithRetry(file, roomData.origin, 3));
        } else {
            generateProcedural(roomData);
        }
    }

    private void generateProcedural(RoomData room) {
        Bukkit.getScheduler().runTask(plugin, () -> {
            World w = room.origin.getWorld();
            int x0 = room.origin.getBlockX();
            int y0 = room.origin.getBlockY();
            int z0 = room.origin.getBlockZ();

            for (int x = 0; x < room.width; x++) {
                for (int y = 0; y < room.height; y++) {
                    for (int z = 0; z < room.depth; z++) {
                        boolean border = x == 0 || x == room.width - 1 || z == 0 || z == room.depth - 1 || y == 0 || y == room.height - 1;
                        org.bukkit.block.Block block = w.getBlockAt(x0 + x, y0 + y, z0 + z);
                        if (border) block.setType(org.bukkit.Material.STONE_BRICKS);
                        else block.setType(org.bukkit.Material.AIR);
                    }
                }
            }
            applyThemeDecor(room);
        });
    }

    private void applyThemeDecor(RoomData room) {
        Bukkit.getScheduler().runTask(plugin, () -> {
            switch (room.theme) {
                case FIRE -> room.origin.getWorld().spawnParticle(org.bukkit.Particle.FLAME, room.getCenter(), 40, 1,1,1);
                case SHADOW -> room.origin.getWorld().spawnParticle(org.bukkit.Particle.SMOKE, room.getCenter(), 40,1,1,1);
                default -> {}
            }
        });
    }
}
