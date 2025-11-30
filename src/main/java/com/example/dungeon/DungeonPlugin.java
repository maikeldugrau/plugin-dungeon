package com.example.dungeon;

import org.bukkit.plugin.java.JavaPlugin;

public class DungeonPlugin extends JavaPlugin {
    @Override
    public void onEnable() {
        getLogger().info("DungeonPlugin enabled.");
    }

    @Override
    public void onDisable() {
        getLogger().info("DungeonPlugin disabled.");
    }
}
