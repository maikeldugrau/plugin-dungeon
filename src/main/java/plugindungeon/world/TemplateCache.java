package plugindungeon.world;

import org.bukkit.plugin.java.JavaPlugin;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

public class TemplateCache {
    private final JavaPlugin plugin;
    private final Map<String, Object> cache = new ConcurrentHashMap<>();
    private final Map<String, Long> timestamps = new ConcurrentHashMap<>();
    private final long ttlMs = 10 * 60 * 1000L;

    public TemplateCache(JavaPlugin plugin) { this.plugin = plugin; }

    public void put(String key, Object data) { cache.put(key, data); timestamps.put(key, System.currentTimeMillis()); }
    public Optional<Object> get(String key) {
        if (!cache.containsKey(key)) return Optional.empty();
        long t = timestamps.getOrDefault(key, 0L);
        if (System.currentTimeMillis() - t > ttlMs) { cache.remove(key); timestamps.remove(key); return Optional.empty(); }
        return Optional.ofNullable(cache.get(key));
    }
    public void clear() { cache.clear(); timestamps.clear(); }
}
