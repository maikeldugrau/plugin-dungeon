package plugindungeon.util;

import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.plugin.java.JavaPlugin;

import java.io.File;

public class ConfigManager {
    private final JavaPlugin plugin;
    private FileConfiguration dungeonsCfg;

    public ConfigManager(JavaPlugin plugin) {
        this.plugin = plugin;
        reloadAll();
    }

    public void reloadAll() {
        try {
            File file = new File(plugin.getDataFolder(), "dungeons.yml");
            if (!file.exists()) plugin.saveResource("dungeons.yml", false);
            dungeonsCfg = YamlConfiguration.loadConfiguration(file);
            plugin.getLogger().info("Configs loaded.");
        } catch (Exception e) { plugin.getLogger().warning("Failed to load configs: " + e.getMessage()); }
    }

    public FileConfiguration get(String name) {
        if ("dungeons.yml".equals(name)) return dungeonsCfg;
        return plugin.getConfig();
    }
}
