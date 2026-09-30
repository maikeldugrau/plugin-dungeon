from pathlib import Path
import re

root = Path("aEventos")

pom = root / "pom.xml"
text = pom.read_text(encoding="utf-8")
text = text.replace("<maven.compiler.source>8</maven.compiler.source>", "<maven.compiler.source>25</maven.compiler.source>")
text = text.replace("<maven.compiler.target>8</maven.compiler.target>", "<maven.compiler.target>25</maven.compiler.target>")
if "<id>papermc</id>" not in text:
    text = text.replace("<repositories>", """<repositories>
        <repository>
            <id>papermc</id>
            <url>https://repo.papermc.io/repository/maven-public/</url>
        </repository>""", 1)
old_spigot = """        <dependency>
            <groupId>org.spigotmc</groupId>
            <artifactId>spigot</artifactId>
            <version>1.8.8-R0.1-SNAPSHOT</version>
            <scope>provided</scope>
        </dependency>"""
paper = """        <dependency>
            <groupId>io.papermc.paper</groupId>
            <artifactId>paper-api</artifactId>
            <version>[26.2.build,)</version>
            <scope>provided</scope>
        </dependency>"""
text = text.replace(old_spigot, paper)
text = text.replace("<version>8.7.0</version>", "<version>13.7.1</version>")
pom.write_text(text, encoding="utf-8")

plugin = root / "src/main/resources/plugin.yml"
text = plugin.read_text(encoding="utf-8")
text = re.sub(r"api-version:\s*[^\n]+", "api-version: '26.2'", text)
plugin.write_text(text, encoding="utf-8")

parser = root / "src/main/java/com/ars3ne/eventos/inventory/utils/SimpleItemParser.java"
text = parser.read_text(encoding="utf-8")
text = text.replace("XEnchantment.DURABILITY.getEnchant()", "XEnchantment.UNBREAKING.get()")
parser.write_text(text, encoding="utf-8")

frog = root / "src/main/java/com/ars3ne/eventos/eventos/Frog.java"
frog.write_text(r'''/*
 * This file is part of aEventos, licensed under the MIT License.
 * Copyright (c) Ars3ne
 * Copyright (c) contributors
 */
package com.ars3ne.eventos.eventos;

import com.ars3ne.eventos.aEventos;
import com.ars3ne.eventos.api.Evento;
import com.ars3ne.eventos.listeners.eventos.FrogListener;
import com.ars3ne.eventos.utils.Cuboid;
import com.iridium.iridiumcolorapi.IridiumColorAPI;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.HandlerList;

import java.util.*;

public class Frog extends Evento {

    private final YamlConfiguration config;
    private final FrogListener listener = new FrogListener();

    private final Map<Block, Material> currentBlocks = new HashMap<>();
    private final Map<Block, BlockData> deletedBlocks = new HashMap<>();
    private final Set<Material> remainingMaterials = new LinkedHashSet<>();

    private final Cuboid cuboid;
    private Block woolBlock;

    private final int start;
    private final int time;
    private final int snowTime;
    private int task;
    private boolean levelHappening;
    private final Random random = new Random();

    public Frog(YamlConfiguration config) {
        super(config);
        this.config = config;
        this.start = config.getInt("Evento.Start");
        this.time = config.getInt("Evento.Time");
        this.snowTime = config.getInt("Evento.Snow");
        this.levelHappening = false;

        World world = aEventos.getInstance().getServer().getWorld(config.getString("Locations.Pos1.world"));
        Location pos1 = new Location(world, config.getDouble("Locations.Pos1.x"), config.getDouble("Locations.Pos1.y"), config.getDouble("Locations.Pos1.z"));
        Location pos2 = new Location(world, config.getDouble("Locations.Pos2.x"), config.getDouble("Locations.Pos2.y"), config.getDouble("Locations.Pos2.z"));
        this.cuboid = new Cuboid(pos1, pos2);
    }

    @Override
    public void start() {
        aEventos.getInstance().getServer().getPluginManager().registerEvents(listener, aEventos.getInstance());
        listener.setEvento();

        currentBlocks.clear();
        deletedBlocks.clear();
        remainingMaterials.clear();

        for (Block block : cuboid.getBlocks()) {
            Material type = block.getType();

            if (type != Material.AIR && type != Material.SNOW_BLOCK) {
                if (type == Material.RED_WOOL) {
                    continue;
                }

                currentBlocks.put(block, type);
                remainingMaterials.add(type);
            } else {
                block.setType(Material.SNOW_BLOCK, false);
            }
        }

        aEventos.getInstance().getServer().getScheduler().scheduleSyncDelayedTask(aEventos.getInstance(), () -> {
            for (Block block : cuboid.getBlocks()) {
                if (block.getType() == Material.SNOW_BLOCK) {
                    block.setType(Material.AIR, false);
                }
            }

            task = Bukkit.getScheduler().scheduleSyncRepeatingTask(aEventos.getInstance(), () -> {
                if (!isHappening()) {
                    Bukkit.getScheduler().cancelTask(task);
                    return;
                }
                if (!levelHappening) {
                    frog();
                }
            }, (time + snowTime) * 20L, 20L);
        }, start * 20L);
    }

    @Override
    public void winner(Player p) {
        for (String s : config.getStringList("Messages.Winner")) {
            aEventos.getInstance().getServer().broadcastMessage(
                    IridiumColorAPI.process(s.replace("&", "§")
                            .replace("@winner", p.getName())
                            .replace("@name", config.getString("Evento.Title")))
            );
        }

        this.setWinner(p);
        this.stop();

        for (String s : config.getStringList("Rewards.Commands")) {
            executeConsoleCommand(p, s.replace("@winner", p.getName()));
        }
    }

    @Override
    public void stop() {
        if (task != 0) {
            Bukkit.getScheduler().cancelTask(task);
            task = 0;
        }

        for (Block block : cuboid.getBlocks()) {
            if (block.getType() == Material.SNOW_BLOCK) {
                block.setType(Material.AIR, false);
            }
        }

        for (Map.Entry<Block, BlockData> entry : deletedBlocks.entrySet()) {
            entry.getKey().setBlockData(entry.getValue().clone(), false);
        }

        HandlerList.unregisterAll(listener);
        this.removePlayers();
    }

    private void frog() {
        if (!isHappening()) {
            return;
        }

        levelHappening = true;

        if (remainingMaterials.size() > 1) {
            List<Material> materials = new ArrayList<>(remainingMaterials);
            Material materialRemove = materials.get(random.nextInt(materials.size()));

            for (Map.Entry<Block, Material> entry : new ArrayList<>(currentBlocks.entrySet())) {
                Block block = entry.getKey();
                if (entry.getValue() == materialRemove && block.getType() == materialRemove) {
                    deletedBlocks.putIfAbsent(block, block.getBlockData().clone());
                    block.setType(Material.SNOW_BLOCK, false);
                }
            }

            aEventos.getInstance().getServer().getScheduler().scheduleSyncDelayedTask(aEventos.getInstance(), () -> {
                if (!isHappening()) {
                    return;
                }

                remainingMaterials.remove(materialRemove);

                for (Block block : new ArrayList<>(deletedBlocks.keySet())) {
                    block.setType(Material.AIR, false);
                    currentBlocks.remove(block);
                }
            }, snowTime * 20L);

            aEventos.getInstance().getServer().getScheduler().runTaskLater(
                    aEventos.getInstance(),
                    () -> levelHappening = false,
                    (time + snowTime) * 20L
            );
            return;
        }

        if (deletedBlocks.isEmpty()) {
            levelHappening = false;
            return;
        }

        List<Block> deleted = new ArrayList<>(deletedBlocks.keySet());
        woolBlock = deleted.get(random.nextInt(deleted.size()));
        woolBlock.setType(Material.RED_WOOL, false);
        listener.setWool();

        for (Block block : deletedBlocks.keySet()) {
            if (!block.equals(woolBlock)) {
                block.setType(Material.SNOW_BLOCK, false);
            }
        }

        for (Player player : getPlayers()) {
            sendWoolMessage(player);
        }
        for (Player player : getSpectators()) {
            sendWoolMessage(player);
        }
    }

    private void sendWoolMessage(Player player) {
        for (String s : config.getStringList("Messages.Wool")) {
            player.sendMessage(
                    IridiumColorAPI.process(s.replace("&", "§")
                            .replace("@name", config.getString("Evento.Title")))
            );
        }
    }

    public Block getWoolBlock() {
        return woolBlock;
    }
}
''', encoding="utf-8")

# Old Material.WEB was renamed long ago and no longer exists.
for java in root.glob("src/main/java/**/*.java"):
    src = java.read_text(encoding="utf-8")
    updated = src.replace("Material.WEB", "Material.COBWEB")
    if updated != src:
        java.write_text(updated, encoding="utf-8")

print("Port base aplicado.")
