package plugindungeon;

import plugindungeon.api.DungeonAPIProvider;
import plugindungeon.commands.DungeonAdminCommand;
import plugindungeon.core.DungeonManager;
import plugindungeon.core.generation.DungeonRoomGenerator;
import plugindungeon.core.generation.RoomTemplateRegistry;
import plugindungeon.util.*;
import plugindungeon.world.AsyncSchematicPaster;
import plugindungeon.world.TemplateCache;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.Arrays;

public class DungeonPlugin extends JavaPlugin {

    private static DungeonPlugin instance;

    private ConfigManager configManager;
    private DebugManager debugManager;
    private TemplateCache templateCache;
    private AsyncSchematicPaster schematicPaster;
    private MobPreloader mobPreloader;
    private RoomTemplateRegistry templateRegistry;
    private DungeonRoomGenerator roomGenerator;
    private DungeonManager dungeonManager;

    @Override
    public void onEnable() {
        instance = this;
        getLogger().info("Starting DungeonPlugin (FULL)...");
        saveDefaultConfig();

        // Managers
        this.configManager = new ConfigManager(this);
        this.debugManager = new DebugManager(this);
        this.templateCache = new TemplateCache(this);
        this.schematicPaster = new AsyncSchematicPaster(this, templateCache);
        this.templateRegistry = new RoomTemplateRegistry(this);
        this.mobPreloader = new MobPreloader(this);
        mobPreloader.preload(Arrays.asList(
                org.bukkit.entity.EntityType.ZOMBIE,
                org.bukkit.entity.EntityType.SKELETON,
                org.bukkit.entity.EntityType.BLAZE,
                org.bukkit.entity.EntityType.GHAST,
                org.bukkit.entity.EntityType.WITHER_SKELETON
        ));

        // Core systems
        this.roomGenerator = new DungeonRoomGenerator(this);
        this.dungeonManager = new DungeonManager(this, roomGenerator);

        // API provider
        DungeonAPIProvider.setAPI(dungeonManager);

        // Commands
        getCommand("dungeon").setExecutor(new DungeonAdminCommand());

        // Events
        getServer().getPluginManager().registerEvents(new DungeonAntiExploit(), this);
        getServer().getPluginManager().registerEvents(new plugindungeon.admin.DungeonAdminGUI(), this);

        // create folders
        createDefaultFolders();

        getLogger().info("DungeonPlugin loaded.");
    }

    @Override
    public void onDisable() {
        getLogger().info("DungeonPlugin disabling...");
        if (dungeonManager != null) dungeonManager.shutdownAll();
    }

    private void createDefaultFolders() {
        java.io.File schem = new java.io.File(getDataFolder(), "schematics");
        if (!schem.exists()) schem.mkdirs();
    }

    public static DungeonPlugin get() { return instance; }
    public ConfigManager getConfigManager() { return configManager; }
    public DebugManager getDebugManager() { return debugManager; }
    public TemplateCache getTemplateCache() { return templateCache; }
    public AsyncSchematicPaster getSchematicPaster() { return schematicPaster; }
    public MobPreloader getMobPreloader() { return mobPreloader; }
    public RoomTemplateRegistry getTemplateRegistry() { return templateRegistry; }
    public DungeonRoomGenerator getRoomGenerator() { return roomGenerator; }
    public DungeonManager getDungeonManager() { return dungeonManager; }
}

