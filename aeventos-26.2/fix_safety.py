#!/usr/bin/env python3
"""Safety hardening for aEventos MCGames Paper 26.2. Run after apply_port.py."""
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]).resolve()
BASE = "src/main/java/com/ars3ne/eventos/"
def read(p):
    return (ROOT / p).read_text(encoding="utf-8")
def write(p, s):
    file = ROOT / p
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(s, encoding="utf-8")
    print("hardened:", p)
def require_replace(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Missing patch target: {label}")
    return text.replace(old, new)

# Disk-backed player snapshot, written before any inventory or gamemode changes.
write(BASE+"manager/EventPlayerStateManager.java", r'''package com.ars3ne.eventos.manager;

import com.ars3ne.eventos.aEventos;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.potion.PotionEffect;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.logging.Level;

/** Persist player state before entering an event and recover it after a crash. */
public final class EventPlayerStateManager {
    private EventPlayerStateManager() {}

    private static File file(Player p) {
        return new File(aEventos.getInstance().getDataFolder(), "player-state/" + p.getUniqueId() + ".yml");
    }

    public static boolean capture(Player p, String eventId) {
        File target = file(p);
        if (target.exists()) {
            p.sendMessage("§c[Evento] Existe um inventário anterior pendente de recuperação. Entre novamente ou avise a equipe.");
            aEventos.getInstance().getLogger().warning("Pending snapshot blocks event entry for " + p.getUniqueId());
            return false;
        }
        try {
            Files.createDirectories(target.toPath().getParent());
            YamlConfiguration cfg = new YamlConfiguration();
            cfg.set("event", eventId);
            cfg.set("uuid", p.getUniqueId().toString());
            cfg.set("inventory.storage", new ArrayList<>(Arrays.asList(p.getInventory().getStorageContents())));
            cfg.set("inventory.armor", new ArrayList<>(Arrays.asList(p.getInventory().getArmorContents())));
            cfg.set("inventory.offhand", p.getInventory().getItemInOffHand().clone());
            cfg.set("player.game-mode", p.getGameMode().name());
            cfg.set("player.allow-flight", p.getAllowFlight());
            cfg.set("player.flying", p.isFlying());
            cfg.set("player.food", p.getFoodLevel());
            cfg.set("player.saturation", p.getSaturation());
            cfg.set("player.exhaustion", p.getExhaustion());
            cfg.set("player.level", p.getLevel());
            cfg.set("player.exp", p.getExp());
            cfg.set("player.fire-ticks", p.getFireTicks());
            cfg.set("player.effects", new ArrayList<>(p.getActivePotionEffects()));

            File temp = new File(target.getParentFile(), target.getName() + ".tmp");
            cfg.save(temp);
            try {
                Files.move(temp.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE);
            } catch (java.nio.file.AtomicMoveNotSupportedException e) {
                Files.move(temp.toPath(), target.toPath());
            }
            return true;
        } catch (IOException | RuntimeException ex) {
            aEventos.getInstance().getLogger().log(Level.SEVERE,
                    "Could not persist event player snapshot for " + p.getUniqueId(), ex);
            return false;
        }
    }

    private static ItemStack[] readItems(YamlConfiguration cfg, String key, int size) {
        List<?> list = cfg.getList(key);
        if (list == null) throw new IllegalStateException("Missing saved inventory section: " + key);
        ItemStack[] result = new ItemStack[size];
        for (int i = 0; i < Math.min(size, list.size()); i++) {
            Object value = list.get(i);
            if (value == null) continue;
            if (!(value instanceof ItemStack)) throw new IllegalStateException("Invalid saved item: " + key + "." + i);
            result[i] = ((ItemStack) value).clone();
        }
        return result;
    }

    public static void restore(Player p, boolean restoreInventory) {
        restore(p, restoreInventory, 0);
    }

    private static void restore(Player p, boolean restoreInventory, int attempts) {
        File target = file(p);
        if (!target.exists() || !p.isOnline()) return;
        if (p.isDead()) {
            if (attempts >= 30) {
                aEventos.getInstance().getLogger().warning("Delayed event snapshot recovery for dead player " + p.getName());
                return; // Saved file remains for recovery on next login.
            }
            if (attempts == 0) {
                Bukkit.getScheduler().runTask(aEventos.getInstance(), () -> {
                    if (p.isOnline() && p.isDead()) p.spigot().respawn();
                });
            }
            Bukkit.getScheduler().runTaskLater(aEventos.getInstance(),
                    () -> restore(p, restoreInventory, attempts + 1), 2L);
            return;
        }

        try {
            YamlConfiguration cfg = YamlConfiguration.loadConfiguration(target);
            if (!p.getUniqueId().toString().equals(cfg.getString("uuid"))) {
                throw new IllegalStateException("Snapshot UUID mismatch");
            }

            // Parse and validate everything before mutating live inventory.
            ItemStack[] storage = restoreInventory ?
                    readItems(cfg, "inventory.storage", p.getInventory().getStorageContents().length) : null;
            ItemStack[] armor = restoreInventory ?
                    readItems(cfg, "inventory.armor", p.getInventory().getArmorContents().length) : null;
            ItemStack offhand = cfg.getItemStack("inventory.offhand");
            GameMode gamemode = GameMode.valueOf(cfg.getString("player.game-mode", "SURVIVAL"));
            List<PotionEffect> effects = new ArrayList<>();
            List<?> rawEffects = cfg.getList("player.effects");
            if (rawEffects != null) {
                for (Object raw : rawEffects) {
                    if (!(raw instanceof PotionEffect)) throw new IllegalStateException("Invalid potion effect in snapshot");
                    effects.add((PotionEffect) raw);
                }
            }

            if (restoreInventory) {
                p.getInventory().clear();
                p.getInventory().setStorageContents(storage);
                p.getInventory().setArmorContents(armor);
                p.getInventory().setItemInOffHand(offhand);
            }

            p.setGameMode(gamemode);
            p.setAllowFlight(cfg.getBoolean("player.allow-flight"));
            if (p.getAllowFlight()) p.setFlying(cfg.getBoolean("player.flying"));
            p.setFoodLevel(cfg.getInt("player.food", 20));
            p.setSaturation((float) cfg.getDouble("player.saturation", 5.0));
            p.setExhaustion((float) cfg.getDouble("player.exhaustion", 0.0));
            p.setLevel(cfg.getInt("player.level", 0));
            p.setExp((float) cfg.getDouble("player.exp", 0.0));
            p.setFireTicks(cfg.getInt("player.fire-ticks", 0));
            for (PotionEffect effect : new ArrayList<>(p.getActivePotionEffects())) {
                p.removePotionEffect(effect.getType());
            }
            for (PotionEffect effect : effects) p.addPotionEffect(effect);
            p.updateInventory();

            // A successful restore is the only place where the snapshot is deleted.
            if (!target.delete()) {
                aEventos.getInstance().getLogger().warning("Recovered state, but snapshot could not be removed: " + target);
            }
        } catch (Exception ex) {
            aEventos.getInstance().getLogger().log(Level.SEVERE,
                    "Could not restore event state of " + p.getUniqueId() + "; snapshot retained at " + target, ex);
        }
    }

    public static void recoverOnJoin(Player p) {
        if (!file(p).exists()) return;
        var event = aEventos.getEventoManager().getEvento();
        if (event != null && (event.getPlayers().contains(p) || event.getSpectators().contains(p))) return;
        // After a restart there is no active event. The saved snapshot takes precedence.
        restore(p, true);
    }
}
''')

# Update the event lifecycle to store and recover the complete player state.
p = BASE+"api/Evento.java"
s = read(p)
s = require_replace(s,
    "import com.ars3ne.eventos.manager.InventorySerializer;",
    "import com.ars3ne.eventos.manager.EventPlayerStateManager;\nimport com.ars3ne.eventos.manager.InventorySerializer;",
    "Evento import")
s = require_replace(s,
    "    public void join(Player p) {\n\n        if(this.empty_inventory) p.getInventory().clear();",
    "    public void join(Player p) {\n\n        if(!EventPlayerStateManager.capture(p, this.identifier)) return;\n        if(this.empty_inventory) p.getInventory().clear();",
    "Evento.join capture")

# The three inventory-only restore blocks are replaced by complete state recovery.
pattern = re.compile(r"""(?m)^([ \t]*)if\(this\.empty_inventory\) \{\s*
(?P<actor>player|p)\.getInventory\(\)\.clear\(\);\s*
if\(aEventos\.getInstance\(\)\.getConfig\(\)\.getBoolean\("Save inventory"\)\) \{\s*
if\((?P=actor)\.isDead\(\)\) (?P=actor)\.spigot\(\)\.respawn\(\);\s*
InventorySerializer\.deserialize\((?P=actor), this\.identifier, (?:false|leaved)\);\s*
\}\s*
\}""", re.MULTILINE)
s,n = pattern.subn(lambda m: m.group(1)+"EventPlayerStateManager.restore("+m.group("actor")+", this.empty_inventory);",s)
if n != 3: raise RuntimeError(f"Expected 3 inventory restore blocks, got {n}")

# Restore player state only *after* clearing event-added potion effects.
potion_clear = """        for(PotionEffect potion: p.getActivePotionEffects()) {
            p.removePotionEffect(potion.getType());
        }"""
# This exists in join and 2 remove variants; must remove in remove variants only.
idx = s.find("    public void remove(Player p)")
if idx < 0: raise RuntimeError("Evento.remove missing")
before,after=s[:idx],s[idx:]
after = after.replace(potion_clear, "", 2)
s = before+after

# Spectators should never lose their original inventory or gamemode.
s = require_replace(s,
    "    public void spectate(Player p) {\n        p.getInventory().clear();",
    "    public void spectate(Player p) {\n        if(!EventPlayerStateManager.capture(p, this.identifier)) return;\n        p.getInventory().clear();",
    "Evento.spectate capture")
spectator_leave = """            spectators.remove(p);
            p.getInventory().clear();
            if(aEventos.getInstance().getConfig().getBoolean("Spectator gamemode")) {
                p.setGameMode(GameMode.SURVIVAL);
            }
            this.teleport(p, "exit");"""
if s.count(spectator_leave) != 3: raise RuntimeError(f"Expected 3 spectator leave variants, got {s.count(spectator_leave)}")
s=s.replace(spectator_leave,
    """            spectators.remove(p);
            EventPlayerStateManager.restore(p, true);
            this.teleport(p, "exit");""")

# restore spectators left at event conclusion, too
s=require_replace(s,
"""        for (Player player : spectators) {
            // TODO: Corrigir erro.
            //player.getInventory().clear();
            this.teleport(player, "exit");
        }""",
"""        for (Player player : spectators) {
            EventPlayerStateManager.restore(player, true);
            this.teleport(player, "exit");
        }""", "Evento.removePlayers spectators")

# preserve saved effects during removal (existing code removed effects after restored)
write(p, s)

# BattleRoyale overrides join(), so apply same safety guard there.
p=BASE+"eventos/BattleRoyale.java"
s=read(p)
pos=s.find("    public void join(Player p) {")
if pos<0: raise RuntimeError("BattleRoyale.join missing")
s=s[:pos]+s[pos:].replace(
    "    public void join(Player p) {",
    """    public void join(Player p) {
        if(!com.ars3ne.eventos.manager.EventPlayerStateManager.capture(p, getIdentifier())) return;""",1)
# Only saved chest slots were restored before; clear all other slots too.
s=require_replace(s,
"""            Chest chest = (Chest) block.getState();
            Map<Integer, ItemStack> items = chests.get(block);

            for(int pos: items.keySet()) {""",
"""            if (!(block.getState() instanceof Chest)) continue;
            Chest chest = (Chest) block.getState();
            Map<Integer, ItemStack> items = chests.get(block);
            chest.getInventory().clear();

            for(int pos: items.keySet()) {""","BattleRoyale chest reset")
write(p,s)

# The existing command serializer writes an obsolete parallel copy; new state
# snapshot must be created only by join(), after all admission checks pass.
p=BASE+"commands/EventoCommand.java"
s=read(p)
s=require_replace(s,
"""                        if(aEventos.getInstance().getConfig().getBoolean("Save inventory")) {
                            InventorySerializer.serialize(p, aEventos.getEventoManager().getEvento().getIdentifier());
                        }else {""",
"""                        if(!aEventos.getInstance().getConfig().getBoolean("Save inventory")) {""",
"Command remove old pre-join serializer")
write(p,s)

# Listener used to early-return before considering crash recovery.
p=BASE+"listeners/EventoListener.java"
s=read(p)
s=require_replace(s,
    "import com.ars3ne.eventos.aEventos;",
    "import com.ars3ne.eventos.aEventos;\nimport com.ars3ne.eventos.manager.EventPlayerStateManager;\nimport org.bukkit.Bukkit;",
    "listener recovery import")
s=require_replace(s,
"""    public void onJoin(PlayerJoinEvent e) {

        if(aEventos.getEventoManager().getEvento() == null) return;""",
"""    public void onJoin(PlayerJoinEvent e) {
        Bukkit.getScheduler().runTaskLater(aEventos.getInstance(), () -> {
            if (e.getPlayer().isOnline()) {
                EventPlayerStateManager.recoverOnJoin(e.getPlayer());
            }
        }, 20L);

        if(aEventos.getEventoManager().getEvento() == null) return;""",
"listener join recovery")
s=require_replace(s,
"""        if(aEventos.getEventoChatManager().getEvento() != null) {
            aEventos.getEventoChatManager().getEvento().leave(e.getPlayer());
        }else {
            // Se o usuário estava no evento, remova-o.""",
"""        if(aEventos.getEventoChatManager().getEvento() != null) {
            aEventos.getEventoChatManager().getEvento().leave(e.getPlayer());
        }
        if(aEventos.getEventoManager().getEvento() != null) {
            // Se o usuário estava no evento, remova-o.""",
"chat event should not mask arena leave")
write(p,s)

# AutoStart was reading Bukkit state and YamlConfiguration from an async thread.
p=BASE+"manager/AutoStarter.java"
s=read(p)
s=require_replace(s,
    "Bukkit.getScheduler().runTaskTimerAsynchronously(aEventos.getInstance(), () -> {",
    "Bukkit.getScheduler().runTaskTimer(aEventos.getInstance(), () -> {",
    "AutoStarter main thread")
write(p,s)

# Disable unsupported guild events instead of awarding meaningless fake-clan wins.
p=BASE+"manager/EventosManager.java"
s=read(p)
needle="""    private boolean verify(YamlConfiguration config) {

        boolean require_pos = false;"""
s=require_replace(s,needle, """    private boolean verify(YamlConfiguration config) {
        String clanHook = aEventos.getInstance().getConfig().getString("Hook", "none");
        EventoType kind = EventoType.getEventoType(config.getString("Evento.Type"));
        if ((kind == EventoType.GUERRA || kind == EventoType.NEXUS) &&
            !("simpleclans".equalsIgnoreCase(clanHook) && aEventos.getInstance().getSimpleClans() != null)) {
            Bukkit.getLogger().warning("[aEventos] Guild event disabled: only functional SimpleClans hook is supported; BetterTeams integration is pending.");
            return false;
        }

        boolean require_pos = false;""","event manager reject non-functional clan modes")
# verify missing world's loaded and same Pos1/2 world
needle="""        // Se alguma das localizações não está definida, cancele o evento e mande uma mensagem para o console.
        return config.getConfigurationSection("Locations.Lobby") != null &&"""
s=require_replace(s,needle, """        for (String point : new String[]{"Lobby", "Entrance", "Exit"}) {
            String worldName = config.getString("Locations." + point + ".world");
            if (worldName == null || Bukkit.getWorld(worldName) == null) {
                Bukkit.getLogger().warning("[aEventos] Event cannot start: missing world for " + point + ": " + worldName);
                return false;
            }
        }
        if (config.getBoolean("Evento.Spectator mode")) {
            String spectatorWorld = config.getString("Locations.Spectator.world");
            if (spectatorWorld == null || Bukkit.getWorld(spectatorWorld) == null) return false;
        }
        if (require_pos) {
            String p1 = config.getString("Locations.Pos1.world");
            String p2 = config.getString("Locations.Pos2.world");
            if (p1 == null || p2 == null || !p1.equals(p2) || Bukkit.getWorld(p1) == null) return false;
        }

        // Se alguma das localizações não está definida, cancele o evento e mande uma mensagem para o console.
        return config.getConfigurationSection("Locations.Lobby") != null &&""","verify worlds")
write(p,s)

# Avoid false 'update available' reports for locally maintained forks.
p="src/main/resources/config.yml"
s=read(p)
s=s.replace("UpdateChecker: true", "UpdateChecker: false")
s=s.replace("AutoStart:\n  Enabled: true", "AutoStart:\n  Enabled: false")
write(p,s)

print("MC Games safety fixes applied")
