#!/usr/bin/env python3
"""Crash-safe Frog arena snapshots (apply after fix_safety.py)."""
from pathlib import Path
import sys
ROOT=Path(sys.argv[1]).resolve()
BASE="src/main/java/com/ars3ne/eventos/"
def read(rel): return (ROOT/rel).read_text(encoding="utf-8")
def write(rel,data):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data,encoding="utf-8"); print("patched:",rel)
def replace_once(s,a,b,label):
    if a not in s: raise RuntimeError("Unable to patch "+label)
    return s.replace(a,b,1)

write(BASE+"manager/FrogArenaBackup.java",r'''package com.ars3ne.eventos.manager;

import com.ars3ne.eventos.aEventos;
import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;

import java.io.*;
import java.nio.file.*;
import java.util.Map;
import java.util.UUID;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;
import java.util.logging.Level;

/** Persist exact BlockData before Frog changes the arena, replay after unexpected shutdown. */
public final class FrogArenaBackup {
    private FrogArenaBackup() {}
    private static File directory() {
        return new File(aEventos.getInstance().getDataFolder(), "arena-backups");
    }

    public static String snapshot(Map<Block, BlockData> blocks) throws IOException {
        if (blocks.isEmpty()) throw new IOException("Empty Frog arena");
        if (blocks.size() > 20000) throw new IOException("Frog snapshot exceeds safe limit");
        Files.createDirectories(directory().toPath());

        String worldName = blocks.keySet().iterator().next().getWorld().getName();
        String id = "frog-" + UUID.randomUUID();
        Path finalFile = directory().toPath().resolve(id + ".dat.gz");
        Path temp = directory().toPath().resolve(id + ".part");

        try (DataOutputStream out = new DataOutputStream(
                new BufferedOutputStream(new GZIPOutputStream(Files.newOutputStream(temp))))) {
            out.writeInt(0x4d434746); // MCGF
            out.writeInt(1);
            out.writeUTF(worldName);
            out.writeInt(blocks.size());
            for (Map.Entry<Block, BlockData> entry : blocks.entrySet()) {
                Block block = entry.getKey();
                if (!worldName.equals(block.getWorld().getName()))
                    throw new IOException("Frog arena spans multiple worlds");
                out.writeInt(block.getX());
                out.writeInt(block.getY());
                out.writeInt(block.getZ());
                out.writeUTF(entry.getValue().getAsString());
            }
        } catch (Exception e) {
            Files.deleteIfExists(temp);
            throw e instanceof IOException ? (IOException) e : new IOException(e);
        }

        try {
            Files.move(temp, finalFile, StandardCopyOption.ATOMIC_MOVE);
        } catch (AtomicMoveNotSupportedException ex) {
            Files.move(temp, finalFile);
        }
        return id;
    }

    public static void complete(String id) {
        if (id == null) return;
        try {
            Files.deleteIfExists(directory().toPath().resolve(id + ".dat.gz"));
        } catch (IOException ex) {
            aEventos.getInstance().getLogger().log(Level.SEVERE, "Could not delete Frog arena journal " + id, ex);
        }
    }

    public static boolean hasPending(World world) {
        File[] backups = directory().listFiles((dir, name) -> name.endsWith(".dat.gz"));
        if (backups == null) return false;
        for (File file : backups) {
            try (DataInputStream in = new DataInputStream(
                    new BufferedInputStream(new GZIPInputStream(Files.newInputStream(file.toPath()))))) {
                if (in.readInt() != 0x4d434746 || in.readInt() != 1) continue;
                if (world.getName().equals(in.readUTF())) return true;
            } catch (IOException e) {
                aEventos.getInstance().getLogger().warning("Unreadable Frog backup: " + file.getName());
                return true; // Fail closed to avoid overwriting unknown backup.
            }
        }
        return false;
    }

    /** Safe to call on plugin enable and on each WorldLoadEvent, always on main thread. */
    public static void recoverAll() {
        File[] backups = directory().listFiles((dir, name) -> name.endsWith(".dat.gz"));
        if (backups == null) return;
        for (File file : backups) {
            try (DataInputStream in = new DataInputStream(
                    new BufferedInputStream(new GZIPInputStream(Files.newInputStream(file.toPath()))))) {
                if (in.readInt() != 0x4d434746 || in.readInt() != 1)
                    throw new IOException("Invalid backup version");
                String worldName = in.readUTF();
                World world = Bukkit.getWorld(worldName);
                if (world == null) continue; // The world may load later via Multiverse.
                int size = in.readInt();
                if (size < 0 || size > 20000) throw new IOException("Invalid backup size: " + size);
                for (int i = 0; i < size; i++) {
                    int x = in.readInt(), y = in.readInt(), z = in.readInt();
                    BlockData data = Bukkit.createBlockData(in.readUTF());
                    world.getBlockAt(x,y,z).setBlockData(data, false);
                }
                Files.delete(file.toPath());
                aEventos.getInstance().getLogger().info("Recovered Frog arena backup " + file.getName());
            } catch (Exception ex) {
                aEventos.getInstance().getLogger().log(Level.SEVERE,
                        "Frog backup recovery incomplete; backup retained: " + file.getName(), ex);
            }
        }
    }
}
''')

p=BASE+"eventos/Frog.java"
s=read(p)
s=replace_once(s,
"import com.ars3ne.eventos.api.Evento;",
"import com.ars3ne.eventos.api.Evento;\nimport com.ars3ne.eventos.manager.FrogArenaBackup;",
"Frog backup import")
s=replace_once(s,
"    private int task = -1;",
"    private int task = -1;\n    private String arenaBackupId;",
"Frog backup field")
s=replace_once(s,
"""        for (Block block : cuboid.getBlocks()) {
            originalBlocks.put(block, block.getBlockData().clone());

            if (block.getType() != Material.AIR""",
"""        if (FrogArenaBackup.hasPending(cuboid.getPoint1().getWorld())) {
            FrogArenaBackup.recoverAll();
            if (FrogArenaBackup.hasPending(cuboid.getPoint1().getWorld())) {
                Bukkit.getLogger().severe("[aEventos] Frog arena has unrecovered backup; event cancelled.");
                this.stop();
                return;
            }
        }

        // Snapshot ALL blocks before modifying ANY block (crash recovery guarantee).
        for (Block block : cuboid.getBlocks()) {
            originalBlocks.put(block, block.getBlockData().clone());
        }
        try {
            arenaBackupId = FrogArenaBackup.snapshot(originalBlocks);
        } catch (java.io.IOException ex) {
            Bukkit.getLogger().severe("[aEventos] Failed to save Frog arena; event cancelled: " + ex.getMessage());
            this.stop();
            return;
        }

        for (Block block : cuboid.getBlocks()) {
            if (block.getType() != Material.AIR""",
"Frog snapshot before mutations")
s=replace_once(s,
"""        for (Map.Entry<Block, BlockData> entry : originalBlocks.entrySet()) {
            entry.getKey().setBlockData(entry.getValue(), false);
        }

        originalBlocks.clear();""",
"""        boolean restored = true;
        for (Map.Entry<Block, BlockData> entry : originalBlocks.entrySet()) {
            try {
                entry.getKey().setBlockData(entry.getValue(), false);
            } catch (Exception ex) {
                restored = false;
                Bukkit.getLogger().severe("[aEventos] Failed to restore Frog block: " + ex.getMessage());
            }
        }
        if (restored) {
            FrogArenaBackup.complete(arenaBackupId);
            arenaBackupId = null;
        }

        originalBlocks.clear();""",
"Frog rollback and journal cleanup")
write(p,s)

p=BASE+"aEventos.java"
s=read(p)
s=replace_once(s,"import com.ars3ne.eventos.manager.", "import com.ars3ne.eventos.manager.", "main imports exists") # presence check
# inject by fully-qualified names to avoid dependence on import details
s=replace_once(s,
"""        setupConfig();

        connection = new ConnectionManager();""",
"""        setupConfig();

        // Restore arenas after a crash, including worlds loaded later by Multiverse.
        com.ars3ne.eventos.manager.FrogArenaBackup.recoverAll();
        getServer().getPluginManager().registerEvents(new org.bukkit.event.Listener() {
            @org.bukkit.event.EventHandler
            public void onWorldLoad(org.bukkit.event.world.WorldLoadEvent event) {
                com.ars3ne.eventos.manager.FrogArenaBackup.recoverAll();
            }
        }, this);

        connection = new ConnectionManager();""",
"onEnable arena recovery")
write(p,s)

# Limit the Frog area to a bounded journal size, too.
p=BASE+"manager/EventosManager.java"
s=read(p).replace("75000", "20000")
write(p,s)
print("Frog crash recovery hardening applied")
