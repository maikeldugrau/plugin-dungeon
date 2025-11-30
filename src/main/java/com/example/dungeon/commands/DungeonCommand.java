package com.example.dungeon.commands;

import com.example.dungeon.DungeonPlugin;
import com.example.dungeon.dungeon.Boss;
import com.example.dungeon.dungeon.DungeonManager;
import com.example.dungeon.dungeon.Miniboss;
import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;

public class DungeonCommand implements CommandExecutor {

    private final DungeonManager dungeonManager = DungeonPlugin.getInstance().getDungeonManager();

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if(args.length == 0) {
            sender.sendMessage(ChatColor.GREEN + "Use: /dungeon generate | boss spawn | miniboss spawn");
            return true;
        }

        switch(args[0].toLowerCase()) {
            case "generate":
                dungeonManager.generateDungeon();
                sender.sendMessage(ChatColor.GREEN + "Dungeon gerada!");
                break;
            case "boss":
                Boss boss = dungeonManager.spawnBoss();
                sender.sendMessage(ChatColor.RED + "Boss final spawnado: " + boss.getName());
                break;
            case "miniboss":
                Miniboss miniboss = dungeonManager.spawnMiniboss();
                sender.sendMessage(ChatColor.YELLOW + "Miniboss spawnado: " + miniboss.getName());
                break;
            default:
                sender.sendMessage(ChatColor.RED + "Subcomando desconhecido.");
        }
        return true;
    }
}

