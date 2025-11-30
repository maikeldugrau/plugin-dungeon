package com.example.dungeon;

import com.example.dungeon.commands.DungeonCommand;
import com.example.dungeon.dungeon.DungeonManager;
import org.bukkit.plugin.java.JavaPlugin;

public class DungeonPlugin extends JavaPlugin {

    private static DungeonPlugin instance;
    private DungeonManager dungeonManager;

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();

        // Inicializa manager de dungeons
        dungeonManager = new DungeonManager();

        // Registra comando principal
        this.getCommand("dungeon").setExecutor(new DungeonCommand());

        getLogger().info("DungeonPlugin habilitado com sucesso!");
    }

    @Override
    public void onDisable() {
        getLogger().info("DungeonPlugin desabilitado!");
    }

    public static DungeonPlugin getInstance() {
        return instance;
    }

    public DungeonManager getDungeonManager() {
        return dungeonManager;
    }
}

