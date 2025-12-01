package plugindungeon.util;

import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitRunnable;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

public class MobPreloader {
    private final JavaPlugin plugin;
    private final Set<EntityType> preloaded = new HashSet<>();

    public MobPreloader(JavaPlugin plugin) { this.plugin = plugin; }

    public void preload(Collection<EntityType> types) {
        new BukkitRunnable() {
            @Override
            public void run() {
                World w = plugin.getServer().getWorlds().get(0);
                for (EntityType t : types) {
                    try {
                        Entity e = w.spawnEntity(w.getSpawnLocation().add(0,2,0), t);
                        e.remove();
                        preloaded.add(t);
                        plugin.getLogger().info("Preloaded mob: " + t.name());
                    } catch (Exception ignored) {}
                }
            }
        }.runTaskAsynchronously(plugin);
    }

    public boolean isPreloaded(EntityType t) { return preloaded.contains(t); }
}
