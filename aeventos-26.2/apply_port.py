#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def write(rel, content):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"patched: {rel}")

# ---- pom.xml: Paper 26.2 + Java 25 + modern build tooling ----
pom = read("pom.xml")
pom = pom.replace("<version>1.5.1</version>", "<version>1.5.1-mcgames-26.2</version>", 1)
pom = pom.replace(
    "<maven.compiler.source>8</maven.compiler.source>\n        <maven.compiler.target>8</maven.compiler.target>",
    "<maven.compiler.release>25</maven.compiler.release>"
)
if "<id>papermc</id>" not in pom:
    pom = pom.replace(
        "<repositories>",
        """<repositories>
        <repository>
            <id>papermc</id>
            <url>https://repo.papermc.io/repository/maven-public/</url>
        </repository>""",
        1,
    )

spigot_dep = re.compile(
    r"""<dependency>\s*
\s*<groupId>org\.spigotmc</groupId>\s*
\s*<artifactId>spigot</artifactId>\s*
\s*<version>1\.8\.8-R0\.1-SNAPSHOT</version>\s*
\s*<scope>provided</scope>\s*
\s*</dependency>""",
    re.MULTILINE,
)
pom, count = spigot_dep.subn(
    """<dependency>
            <groupId>io.papermc.paper</groupId>
            <artifactId>paper-api</artifactId>
            <version>[26.2.build,)</version>
            <scope>provided</scope>
        </dependency>""",
    pom,
    count=1,
)
if count != 1:
    raise SystemExit("Could not replace the legacy Spigot dependency in pom.xml")

# Remove a dead Maven repository that causes dependency resolution to abort.
pom = pom.replace("""        <repository>
            <id>2lstudios</id>
            <url>https://ci.2lstudios.dev/plugin/repository/everything/</url>
        </repository>
""", "")
pom = pom.replace("""        <repository>
            <id>savagelabs</id>
            <url>https://nexus.savagelabs.net/repository/maven-releases/</url>
        </repository>
""", "")
pom = pom.replace("<version>8.7.0</version>", "<version>13.7.1</version>", 1)
pom = pom.replace("<version>3.2.4</version>", "<version>3.6.1</version>", 1)

if "<artifactId>maven-compiler-plugin</artifactId>" not in pom:
    pom = pom.replace(
        "<plugins>",
        """<plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.14.1</version>
                <configuration>
                    <release>25</release>
                </configuration>
            </plugin>""",
        1,
    )

write("pom.xml", pom)

# ---- plugin metadata ----
plugin_yml = read("src/main/resources/plugin.yml")
plugin_yml = re.sub(r"(?m)^api-version:\s*.*$", "api-version: '26.2'", plugin_yml)
write("src/main/resources/plugin.yml", plugin_yml)

# ---- Frog: remove pre-flattening byte data and restore exact BlockData ----
frog = r'''/*
 *
 * This file is part of aEventos, licensed under the MIT License.
 *
 * Copyright (c) Ars3ne
 * Copyright (c) contributors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

public class Frog extends Evento {

    private final YamlConfiguration config;
    private final FrogListener listener = new FrogListener();

    /*
     * Paper 26.2-only implementation:
     * - BlockData replaces the removed legacy byte data API.
     * - The complete arena is snapshotted and restored on stop, preventing
     *   AIR/SNOW blocks from being permanently modified by an event.
     */
    private final Map<Block, BlockData> originalBlocks = new HashMap<>();
    private final Map<Block, BlockData> activeBlocks = new HashMap<>();
    private final Map<Block, BlockData> deletedBlocks = new HashMap<>();
    private final Set<Material> remainingMaterials = new LinkedHashSet<>();

    private final Cuboid cuboid;
    private Block woolBlock;

    private final int start;
    private final int time;
    private final int snowTime;
    private int task = -1;
    private boolean levelHappening;
    private final Random random = new Random();

    public Frog(YamlConfiguration config) {
        super(config);

        this.config = config;
        this.start = config.getInt("Evento.Start");
        this.time = config.getInt("Evento.Time");
        this.snowTime = config.getInt("Evento.Snow");

        World world = aEventos.getInstance().getServer().getWorld(config.getString("Locations.Pos1.world"));
        if (world == null) {
            throw new IllegalArgumentException("Mundo do evento Frog não encontrado: " + config.getString("Locations.Pos1.world"));
        }

        Location pos1 = new Location(world,
                config.getDouble("Locations.Pos1.x"),
                config.getDouble("Locations.Pos1.y"),
                config.getDouble("Locations.Pos1.z"));
        Location pos2 = new Location(world,
                config.getDouble("Locations.Pos2.x"),
                config.getDouble("Locations.Pos2.y"),
                config.getDouble("Locations.Pos2.z"));
        this.cuboid = new Cuboid(pos1, pos2);
    }

    @Override
    public void start() {
        aEventos.getInstance().getServer().getPluginManager().registerEvents(listener, aEventos.getInstance());
        listener.setEvento();

        originalBlocks.clear();
        activeBlocks.clear();
        deletedBlocks.clear();
        remainingMaterials.clear();
        woolBlock = null;
        levelHappening = false;

        for (Block block : cuboid.getBlocks()) {
            originalBlocks.put(block, block.getBlockData().clone());

            if (block.getType() != Material.AIR && block.getType() != Material.SNOW_BLOCK) {
                if (block.getType() == Material.RED_WOOL) {
                    continue;
                }

                activeBlocks.put(block, block.getBlockData().clone());
                remainingMaterials.add(block.getType());
            } else {
                block.setType(Material.SNOW_BLOCK, false);
            }
        }

        aEventos.getInstance().getServer().getScheduler().scheduleSyncDelayedTask(aEventos.getInstance(), () -> {
            if (!isHappening()) {
                return;
            }

            for (Block block : cuboid.getBlocks()) {
                if (block.getType() == Material.SNOW_BLOCK) {
                    block.setType(Material.AIR, false);
                }
            }

            task = Bukkit.getScheduler().scheduleSyncRepeatingTask(aEventos.getInstance(), () -> {
                if (!isHappening()) {
                    if (task != -1) {
                        Bukkit.getScheduler().cancelTask(task);
                    }
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
        List<String> broadcastMessages = config.getStringList("Messages.Winner");
        for (String s : broadcastMessages) {
            aEventos.getInstance().getServer().broadcastMessage(
                    IridiumColorAPI.process(
                            s.replace("&", "§")
                                    .replace("@winner", p.getName())
                                    .replace("@name", config.getString("Evento.Title"))
                    )
            );
        }

        this.setWinner(p);
        this.stop();

        List<String> commands = config.getStringList("Rewards.Commands");
        for (String s : commands) {
            executeConsoleCommand(p, s.replace("@winner", p.getName()));
        }
    }

    @Override
    public void stop() {
        if (task != -1) {
            Bukkit.getScheduler().cancelTask(task);
            task = -1;
        }

        for (Map.Entry<Block, BlockData> entry : originalBlocks.entrySet()) {
            entry.getKey().setBlockData(entry.getValue(), false);
        }

        originalBlocks.clear();
        activeBlocks.clear();
        deletedBlocks.clear();
        remainingMaterials.clear();
        woolBlock = null;
        levelHappening = false;

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

            for (Map.Entry<Block, BlockData> entry : new ArrayList<>(activeBlocks.entrySet())) {
                Block block = entry.getKey();
                if (block.getType() == materialRemove) {
                    deletedBlocks.putIfAbsent(block, entry.getValue().clone());
                    block.setType(Material.SNOW_BLOCK, false);
                }
            }

            aEventos.getInstance().getServer().getScheduler().scheduleSyncDelayedTask(aEventos.getInstance(), () -> {
                if (!isHappening()) {
                    return;
                }

                remainingMaterials.remove(materialRemove);

                for (Block block : new ArrayList<>(deletedBlocks.keySet())) {
                    if (block != woolBlock) {
                        block.setType(Material.AIR, false);
                    }
                    activeBlocks.remove(block);
                }
            }, snowTime * 20L);

            aEventos.getInstance().getServer().getScheduler().runTaskLater(
                    aEventos.getInstance(),
                    () -> levelHappening = false,
                    (time + snowTime) * 20L
            );

        } else {
            if (deletedBlocks.isEmpty()) {
                levelHappening = false;
                return;
            }

            List<Block> deletedBlocksArray = new ArrayList<>(deletedBlocks.keySet());
            woolBlock = deletedBlocksArray.get(random.nextInt(deletedBlocksArray.size()));
            woolBlock.setType(Material.RED_WOOL, false);
            listener.setWool();

            for (Block block : deletedBlocks.keySet()) {
                if (block != woolBlock) {
                    block.setType(Material.SNOW_BLOCK, false);
                }
            }

            List<String> woolMessages = config.getStringList("Messages.Wool");
            for (Player player : getPlayers()) {
                for (String s : woolMessages) {
                    player.sendMessage(
                            IridiumColorAPI.process(
                                    s.replace("&", "§").replace("@name", config.getString("Evento.Title"))
                            )
                    );
                }
            }

            for (Player player : getSpectators()) {
                for (String s : woolMessages) {
                    player.sendMessage(
                            IridiumColorAPI.process(
                                    s.replace("&", "§").replace("@name", config.getString("Evento.Title"))
                            )
                    );
                }
            }
        }
    }

    public Block getWoolBlock() {
        return woolBlock;
    }
}
'''
write("src/main/java/com/ars3ne/eventos/eventos/Frog.java", frog)

# ---- SimpleItemParser: public Paper profiles, no GameProfile reflection ----
parser = r'''/*
 *
 * This file is part of aEventos, licensed under the MIT License.
 *
 * Copyright (c) Ars3ne
 * Copyright (c) contributors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */

package com.ars3ne.eventos.inventory.utils;

import com.cryptomorin.xseries.XMaterial;
import com.destroystokyo.paper.profile.PlayerProfile;
import com.destroystokyo.paper.profile.ProfileProperty;
import org.bukkit.Bukkit;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.inventory.ItemFlag;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.inventory.meta.SkullMeta;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class SimpleItemParser {

    public static ItemStack parse(ConfigurationSection section, Map<String, String> placeholders) {
        String configuredMaterial = section.getString("Material");
        XMaterial xMaterial = XMaterial.matchXMaterial(configuredMaterial)
                .orElseThrow(() -> new IllegalArgumentException("Material inválido no menu: " + configuredMaterial));

        ItemStack item = xMaterial.parseItem();
        if (item == null) {
            throw new IllegalArgumentException("Não foi possível criar o material do menu: " + configuredMaterial);
        }

        ItemMeta meta = item.getItemMeta();
        if (meta == null) {
            return item;
        }

        String configuredName = section.getString("Name");
        if (configuredName != null) {
            String name = applyPlaceholders(configuredName, placeholders);
            meta.setDisplayName(name.replace("&", "§"));
        }

        List<String> configuredLore = section.getStringList("Lore");
        if (!configuredLore.isEmpty()) {
            List<String> lore = new ArrayList<>();
            for (String line : configuredLore) {
                lore.add(applyPlaceholders(line, placeholders).replace("&", "§"));
            }
            meta.setLore(lore);
        }

        if (section.getBoolean("Glow")) {
            meta.addEnchant(Enchantment.UNBREAKING, 1, true);
            meta.addItemFlags(ItemFlag.HIDE_ENCHANTS);
        }

        item.setItemMeta(meta);

        if (xMaterial == XMaterial.PLAYER_HEAD) {
            SkullMeta skullMeta = (SkullMeta) item.getItemMeta();
            if (skullMeta == null) {
                return item;
            }

            String headData = applyPlaceholders(section.getString("Head data", ""), placeholders);

            if (section.getBoolean("Custom head")) {
                setCustomTexture(skullMeta, "http://textures.minecraft.net/texture/" + headData);
            } else if (!headData.isBlank()) {
                skullMeta.setOwningPlayer(Bukkit.getOfflinePlayer(headData));
            }

            item.setItemMeta(skullMeta);
        }

        return item;
    }

    private static String applyPlaceholders(String text, Map<String, String> placeholders) {
        if (text == null || placeholders == null) {
            return text == null ? "" : text;
        }

        String result = text;
        for (Map.Entry<String, String> entry : placeholders.entrySet()) {
            result = result.replace(entry.getKey(), entry.getValue());
        }
        return result;
    }

    private static void setCustomTexture(SkullMeta meta, String url) {
        PlayerProfile profile = Bukkit.createProfile(UUID.randomUUID());
        String json = String.format("{textures:{SKIN:{url:\"%s\"}}}", url);
        String data = Base64.getEncoder().encodeToString(json.getBytes(StandardCharsets.UTF_8));
        profile.setProperty(new ProfileProperty("textures", data));
        meta.setPlayerProfile(profile);
    }
}
'''
write("src/main/java/com/ars3ne/eventos/inventory/utils/SimpleItemParser.java", parser)

# Modernize the top menu's player-head owner assignment. This is API-safe on 26.2.
top_path = "src/main/java/com/ars3ne/eventos/inventory/EventoTopInventory.java"
top = read(top_path)
top = top.replace("meta.setOwner(p.getName());", "meta.setOwningPlayer(p);")
write(top_path, top)

# A small source marker for operators.
readme = ROOT / "MCGAMES-26.2-PORT.md"
readme.write_text(
    """# aEventos — MC Games Paper 26.2 port

Base: Ars3ne/aEventos 1.5.1 (MIT)

Port changes:
- Paper API 26.2
- Java 25
- XSeries 13.7.1
- plugin.yml api-version 26.2
- Frog migrated from legacy material bytes to BlockData
- Frog now restores the complete arena snapshot on stop
- custom player heads migrated away from GameProfile reflection
- glow enchant uses Bukkit Enchantment.UNBREAKING
- player-head owner assignment uses OfflinePlayer API

This is a compatibility port. Validate every event on a staging server before production use.
""",
    encoding="utf-8",
)
print("port patch complete")
