from pathlib import Path
import re

root = Path("aEventos")

# pom.xml
pom = (root/"pom.xml").read_text(encoding="utf-8")
pom = pom.replace("<version>1.5.1</version>", "<version>1.5.1-MCGames-26.2</version>", 1)
pom = pom.replace("<maven.compiler.source>8</maven.compiler.source>", "<maven.compiler.source>25</maven.compiler.source>")
pom = pom.replace("<maven.compiler.target>8</maven.compiler.target>", "<maven.compiler.target>25</maven.compiler.target>")
pom = re.sub(
    r'<repository>\s*<id>spigot-repo</id>\s*<url>https://hub\.spigotmc\.org/nexus/content/repositories/snapshots/</url>\s*</repository>',
    '<repository>\n            <id>papermc</id>\n            <url>https://repo.papermc.io/repository/maven-public/</url>\n        </repository>',
    pom,
    count=1
)
pom = re.sub(
    r'<dependency>\s*<groupId>org\.spigotmc</groupId>\s*<artifactId>spigot</artifactId>\s*<version>1\.8\.8-R0\.1-SNAPSHOT</version>\s*<scope>provided</scope>\s*</dependency>',
    '<dependency>\n            <groupId>io.papermc.paper</groupId>\n            <artifactId>paper-api</artifactId>\n            <version>26.2-R0.1-SNAPSHOT</version>\n            <scope>provided</scope>\n        </dependency>',
    pom,
    count=1
)
pom = pom.replace("<version>8.7.0</version>", "<version>13.7.1</version>")
pom = pom.replace("<version>3.2.4</version>", "<version>3.6.0</version>")
(root/"pom.xml").write_text(pom, encoding="utf-8")

# plugin.yml
plugin = root/"src/main/resources/plugin.yml"
s = plugin.read_text(encoding="utf-8")
s = s.replace("api-version: 1.13", "api-version: '26.2'")
plugin.write_text(s, encoding="utf-8")

# SimpleItemParser - modern Bukkit profiles + Enchantment
p = root/"src/main/java/com/ars3ne/eventos/inventory/utils/SimpleItemParser.java"
s = p.read_text(encoding="utf-8")
s = s.replace("import com.cryptomorin.xseries.XEnchantment;\n", "")
s = s.replace("import com.mojang.authlib.GameProfile;\n", "")
s = s.replace("import com.mojang.authlib.properties.Property;\n", "")
s = s.replace("import org.bukkit.configuration.ConfigurationSection;\n", "import org.bukkit.Bukkit;\nimport org.bukkit.configuration.ConfigurationSection;\n")
s = s.replace("import org.bukkit.inventory.ItemFlag;\n", "import org.bukkit.enchantments.Enchantment;\nimport org.bukkit.inventory.ItemFlag;\n")
s = s.replace("import java.lang.reflect.Field;\n", "")
s = s.replace("import java.util.*;\n", "import java.net.MalformedURLException;\nimport java.net.URL;\nimport java.util.*;\n")
s = s.replace("meta.addEnchant(XEnchantment.DURABILITY.getEnchant(), 1, false);", "meta.addEnchant(Enchantment.UNBREAKING, 1, true);")
s = s.replace("skull_meta.setOwner(owner);", "skull_meta.setOwningPlayer(Bukkit.getOfflinePlayer(owner));")

start = s.index("    private static ItemStack getCustomSkull")
end = s.rindex("\n}")
method = '''    private static ItemStack getCustomSkull(String url, ItemStack item) {
        SkullMeta meta = (SkullMeta) item.getItemMeta();
        if (meta == null) return item;

        try {
            org.bukkit.profile.PlayerProfile profile = Bukkit.createPlayerProfile(UUID.randomUUID());
            org.bukkit.profile.PlayerTextures textures = profile.getTextures();
            textures.setSkin(new URL(url));
            profile.setTextures(textures);
            meta.setOwnerProfile(profile);
            item.setItemMeta(meta);
        } catch (MalformedURLException e) {
            throw new IllegalArgumentException("Invalid custom head URL: " + url, e);
        }

        return item;
    }
'''
s = s[:start] + method + s[end:]
p.write_text(s, encoding="utf-8")

# Frog - 26.2 only, remove data-byte compatibility
p = root/"src/main/java/com/ars3ne/eventos/eventos/Frog.java"
s = p.read_text(encoding="utf-8")
s = s.replace("import com.cryptomorin.xseries.XMaterial;\n", "")
s = s.replace("import com.google.common.collect.ArrayListMultimap;\n", "")
s = s.replace("import com.google.common.collect.Multimap;\n", "")
s = s.replace("import org.bukkit.configuration.file.YamlConfiguration;\n", "import org.bukkit.block.data.BlockData;\nimport org.bukkit.configuration.file.YamlConfiguration;\n")
s = s.replace("    private final Map<Block, Material> current_blocks = new HashMap<>();\n    private final Map<Block, Map<Material, Byte>> deleted_blocks = new HashMap<>();\n    private final Multimap<Material, Byte> remeaning_materials = ArrayListMultimap.create();",
              "    private final Map<Block, Material> current_blocks = new HashMap<>();\n    private final Map<Block, BlockData> deleted_blocks = new HashMap<>();\n    private final List<Material> remeaning_materials = new ArrayList<>();")
s = s.replace("                if(!XMaterial.isNewVersion() && block.getType() == XMaterial.RED_WOOL.parseMaterial() && block.getData() == XMaterial.RED_WOOL.getData()) continue;\n                else if(XMaterial.isNewVersion() && block.getType() == XMaterial.RED_WOOL.parseMaterial()) continue;\n\n", "                if (block.getType() == Material.RED_WOOL) continue;\n\n")
old = '''                if(remeaning_materials.containsKey(block.getType()) && !XMaterial.isNewVersion()) {

                    boolean exists = false;

                    for(byte mat: remeaning_materials.get(block.getType())) {
                        if(mat == block.getData()) exists = true;
                    }

                   if(!exists) remeaning_materials.put(block.getType(), block.getData());
                   continue;

                }else if(!XMaterial.isNewVersion()){
                    remeaning_materials.put(block.getType(), block.getData());
                }

                if(XMaterial.isNewVersion() && !remeaning_materials.containsKey(block.getType())) remeaning_materials.put(block.getType(), (byte) 0);
'''
s = s.replace(old, "                if (!remeaning_materials.contains(block.getType())) remeaning_materials.add(block.getType());\n")
old = '''        for(Block block: deleted_blocks.keySet()) {
            Map<Material, Byte> hash = deleted_blocks.get(block);
            block.setType((Material) hash.keySet().toArray()[0]);
            if(!XMaterial.isNewVersion()) block.setData((Byte) hash.values().toArray()[0]);
        }
'''
s = s.replace(old, '''        for (Map.Entry<Block, BlockData> entry : deleted_blocks.entrySet()) {
            entry.getKey().setBlockData(entry.getValue(), false);
        }
''')
s = s.replace("            Material material_remove = (Material) remeaning_materials.keys().toArray()[index];\n            byte material_data = (byte) remeaning_materials.values().toArray()[index];",
              "            Material material_remove = remeaning_materials.get(index);")
s = s.replace("                if(b.getType() == material_remove && (material_data == (byte) 0 || material_data == b.getData())) {\n\n                    HashMap<Material, Byte> hash = new HashMap<>();\n                    hash.put(material_remove, material_data);\n\n                    deleted_blocks.put(b, hash);",
              "                if (b.getType() == material_remove) {\n                    deleted_blocks.putIfAbsent(b, b.getBlockData().clone());")
s = s.replace("                remeaning_materials.remove(material_remove, material_data);", "                remeaning_materials.remove(material_remove);")
s = s.replace("            wool_block.setType(XMaterial.RED_WOOL.parseMaterial());\n            if(!XMaterial.isNewVersion()) wool_block.setData(XMaterial.RED_WOOL.getData());", "            wool_block.setType(Material.RED_WOOL);")
p.write_text(s, encoding="utf-8")

# Common legacy material name
for p in root.rglob("*.java"):
    s = p.read_text(encoding="utf-8")
    ns = s.replace("Material.WEB", "Material.COBWEB")
    if ns != s:
        p.write_text(ns, encoding="utf-8")

print("Port patches applied")
