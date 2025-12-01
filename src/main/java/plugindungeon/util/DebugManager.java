package plugindungeon.util;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.plugin.java.JavaPlugin;

public class DebugManager implements CommandExecutor {
    private final JavaPlugin plugin;
    private boolean debug = false;

    public DebugManager(JavaPlugin plugin) {
        this.plugin = plugin;
        try { plugin.getCommand("dgdebug").setExecutor(this); } catch (Exception ignored) {}
    }

    public void log(String tag, String msg) {
        if (debug) plugin.getLogger().info("[DEBUG][" + tag + "] " + msg);
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("dungeon.admin")) return true;
        if (args.length == 0) { sender.sendMessage("Debug: " + (debug ? "ON" : "OFF")); return true; }
        if ("on".equalsIgnoreCase(args[0])) { debug = true; sender.sendMessage("Debug ligado"); }
        else if ("off".equalsIgnoreCase(args[0])) { debug = false; sender.sendMessage("Debug desligado"); }
        return true;
    }
}
