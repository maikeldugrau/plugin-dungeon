package plugindungeon.admin;

import org.bukkit.Bukkit;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.entity.Player;
import org.bukkit.Material;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

public class DungeonAdminGUI implements Listener {

    public static void open(Player p) {
        Inventory inv = Bukkit.createInventory(null, 27, "§8Dungeon Admin");
        inv.setItem(10, createItem(Material.EMERALD, "§aGerar Dungeon"));
        inv.setItem(13, createItem(Material.BOOK, "§eListar Dungeons"));
        inv.setItem(16, createItem(Material.REDSTONE, "§cForçar Próxima Sala"));
        p.openInventory(inv);
    }

    private static ItemStack createItem(Material m, String name) {
        ItemStack it = new ItemStack(m);
        ItemMeta meta = it.getItemMeta();
        meta.setDisplayName(name);
        it.setItemMeta(meta);
        return it;
    }

    @EventHandler
    public void onClick(InventoryClickEvent e) {
        if (!e.getView().getTitle().equals("§8Dungeon Admin")) return;
        e.setCancelled(true);
        if (!(e.getWhoClicked() instanceof Player p)) return;
        switch (e.getRawSlot()) {
            case 10: DungeonAdminGUI.open(p); break;
            case 13:
                p.sendMessage("Dungeons ativas:");
                // TODO listar
                break;
            case 16:
                p.sendMessage("Use /dungeon tp <id>");
                break;
        }
        p.closeInventory();
    }
}
