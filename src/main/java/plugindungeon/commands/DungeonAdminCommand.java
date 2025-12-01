package plugindungeon.commands;

import plugindungeon.DungeonPlugin;
import plugindungeon.api.DungeonAPIProvider;
import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import plugindungeon.core.DungeonManager;

public class DungeonAdminCommand implements CommandExecutor {

    private final DungeonManager dungeonManager = DungeonPlugin.get().getDungeonManager();

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("dungeon.admin")) {
            sender.sendMessage("§cSem permissão.");
            return true;
        }

        if (args.length == 0) {
            sender.sendMessage("§e/dungeon gen <levels> - gerar dungeon");
            sender.sendMessage("§e/dungeon genhere <levels> - gerar aqui");
            sender.sendMessage("§e/dungeon boss spawn - spawn boss");
            sender.sendMessage("§e/dungeon preview <size> - preview");
            sender.sendMessage("§e/dungeon tp <id> - teleportar");
            return true;
        }

        switch (args[0].toLowerCase()) {
            case "gen":
                if (!(sender instanceof Player p)) { sender.sendMessage("Somente players."); return true; }
                int lvl = args.length > 1 ? Integer.parseInt(args[1]) : 1;
                String id = DungeonAPIProvider.get().generateDungeon(p.getLocation(), lvl, 3, 6);
                sender.sendMessage("§aDungeon gerada: " + id);
                break;
            case "genhere":
                if (!(sender instanceof Player p2)) { sender.sendMessage("Somente players."); return true; }
                int l2 = args.length > 1 ? Integer.parseInt(args[1]) : 1;
                String id2 = DungeonAPIProvider.get().generateDungeon(((Player)sender).getLocation(), l2, 3, 6);
                sender.sendMessage("§aDungeon gerada: " + id2);
                break;
            case "boss":
                if (args.length > 1 && args[1].equalsIgnoreCase("spawn")) {
                    DungeonPlugin.get().getDungeonManager().forceSpawnBossPreview(((Player)sender).getLocation());
                    sender.sendMessage("§aBoss spawnado (preview).");
                }
                break;
            case "tp":
                if (args.length < 2) { sender.sendMessage("Uso: /dungeon tp <id>"); return true; }
                DungeonAPIProvider.get().teleportPlayerToDungeon((Player)sender, args[1]);
                sender.sendMessage("§aTeleportado.");
                break;
            default:
                sender.sendMessage("Subcomando desconhecido.");
        }
        return true;
    }
}
