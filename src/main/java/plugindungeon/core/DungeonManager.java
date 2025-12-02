package plugindungeon.core;

import plugindungeon.DungeonPlugin;
import plugindungeon.api.DungeonAPI;
import plugindungeon.api.listeners.*;
import plugindungeon.core.generation.DungeonRoomGenerator;
import plugindungeon.core.generation.RoomData;
import plugindungeon.loot.LootIntegrator;
import plugindungeon.mobs.LordeCataclismo;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Player;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Implementação central da API de dungeons.
 * - Garante registro de listeners
 * - Gerencia dungeons ativas
 * - Integra com o gerador de salas (DungeonRoomGenerator)
 * - Exponha métodos administrativos (teleporte, shutdown, preview de boss)
 */
public class DungeonManager implements DungeonAPI {

    private final DungeonPlugin plugin;
    private final DungeonRoomGenerator generator;
    private final LootIntegrator lootIntegrator;

    // mapa de dungeons ativas -> lista de RoomData
    private final Map<String, List<RoomData>> activeDungeons = new ConcurrentHashMap<>();

    // listeners
    private final List<DungeonStartListener> startListeners = Collections.synchronizedList(new ArrayList<>());
    private final List<DungeonCompleteListener> completeListeners = Collections.synchronizedList(new ArrayList<>());
    private final List<DungeonFailListener> failListeners = Collections.synchronizedList(new ArrayList<>());
    private final List<DungeonLevelUpListener> levelUpListeners = Collections.synchronizedList(new ArrayList<>());

    private final List<DungeonMobDeathListener> mobDeathListeners = Collections.synchronizedList(new ArrayList<>());
    private final List<DungeonBossDeathListener> bossDeathListeners = Collections.synchronizedList(new ArrayList<>());
    private final List<DungeonLootGenerateListener> lootListeners = Collections.synchronizedList(new ArrayList<>());
    private final List<DungeonRoomGenerateListener> roomListeners = Collections.synchronizedList(new ArrayList<>());

    /**
     * Construtor principal — use este construtor no onEnable() do plugin:
     * new DungeonManager(this, roomGenerator);
     */
    public DungeonManager(DungeonPlugin plugin, DungeonRoomGenerator generator) {
        this.plugin = plugin;
        this.generator = generator;
        this.lootIntegrator = new LootIntegrator(plugin);
    }

    // ---------------------------
    // Registro de listeners
    // ---------------------------

    @Override
    public void registerDungeonStartListener(DungeonStartListener listener) {
        startListeners.add(listener);
    }

    @Override
    public void registerDungeonCompleteListener(DungeonCompleteListener listener) {
        completeListeners.add(listener);
    }

    @Override
    public void registerDungeonFailListener(DungeonFailListener listener) {
        failListeners.add(listener);
    }

    @Override
    public void registerDungeonLevelUpListener(DungeonLevelUpListener listener) {
        levelUpListeners.add(listener);
    }

    @Override
    public void registerDungeonMobDeathListener(DungeonMobDeathListener listener) {
        mobDeathListeners.add(listener);
    }

    @Override
    public void registerDungeonBossDeathListener(DungeonBossDeathListener listener) {
        bossDeathListeners.add(listener);
    }

    @Override
    public void registerDungeonLootGenerateListener(DungeonLootGenerateListener listener) {
        lootListeners.add(listener);
    }

    @Override
    public void registerDungeonRoomGenerateListener(DungeonRoomGenerateListener listener) {
        roomListeners.add(listener);
    }

    /**
     * Remove todos os listeners registrados (implementação simples).
     * Se desejar remoção por plugin específico, podemos trocar para map(plugin -> listeners).
     */
    @Override
    public void unregisterAllListeners(Object pluginInstance) {
        startListeners.clear();
        completeListeners.clear();
        failListeners.clear();
        levelUpListeners.clear();
        mobDeathListeners.clear();
        bossDeathListeners.clear();
        lootListeners.clear();
        roomListeners.clear();
    }

    // ---------------------------
    // Control API
    // ---------------------------

    @Override
    public boolean startDungeon(String dungeonId, String playerName) {
        Player player = Bukkit.getPlayer(playerName);
        if (player == null) {
            plugin.getLogger().warning("[DungeonPlugin] Jogador não encontrado: " + playerName);
            return false;
        }

        player.sendMessage("§aIniciando dungeon §f" + dungeonId);
        for (DungeonStartListener l : snapshot(startListeners)) {
            try { l.onDungeonStart(dungeonId, player); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonStart: " + t.getMessage()); }
        }
        return true;
    }

    // ---------------------------
    // Dungeon management
    // ---------------------------

    /**
     * Gera uma dungeon usando o DungeonRoomGenerator.
     * Retorna um id simples (UUID) para identificar a dungeon.
     */
    @Override
    public String generateDungeon(Location origin, int levels, int minRooms, int maxRooms) {
        // Delegar ao generator (se o generator retornar id, prefira usar o retorno dele)
        String id;
        try {
            id = generator.generateDungeon(origin, levels, minRooms, maxRooms);
            if (id == null || id.isEmpty()) id = UUID.randomUUID().toString();
        } catch (Throwable t) {
            // Em caso de generator personalizado não disponível, crie um id e registre vazio
            plugin.getLogger().warning("Falha ao usar DungeonRoomGenerator: " + t.getMessage());
            id = UUID.randomUUID().toString();
        }

        // inicialmente cria lista vazia; o generator pode publicar RoomData posteriormente via integração
        activeDungeons.putIfAbsent(id, Collections.synchronizedList(new ArrayList<>()));

        // notificar listeners de room generation não aqui — generator deve emitir
        plugin.getLogger().info("Dungeon generated id=" + id + " at " + origin);
        return id;
    }

    @Override
    public List<RoomData> getActiveRooms(String dungeonId) {
        List<RoomData> rooms = activeDungeons.get(dungeonId);
        if (rooms == null) return Collections.emptyList();
        return Collections.unmodifiableList(new ArrayList<>(rooms));
    }

    @Override
    public void triggerNextRoom(String dungeonId) {
        plugin.getLogger().info("Trigger next room requested for dungeon: " + dungeonId);
        // Implementação básica: avança estado em armazenamento ou push evento
        // Para integração completa, chame generator/progression system aqui.
    }

    @Override
    public void teleportPlayerToDungeon(Player player, String dungeonId) {
        List<RoomData> rooms = activeDungeons.get(dungeonId);
        if (rooms != null && !rooms.isEmpty()) {
            // Teleporta para o centro da primeira sala ativa
            RoomData first = rooms.get(0);
            Location center = first.getCenter();
            if (center != null) {
                player.teleport(center);
                return;
            }
        }

        // Fallback - teleporta para spawn do mundo principal
        player.teleport(Bukkit.getWorlds().get(0).getSpawnLocation());
    }

    @Override
    public void shutdownAll() {
        plugin.getLogger().info("Shutting down all dungeons...");
        // limpar dungeons e liberar recursos
        activeDungeons.clear();
        // aqui você pode cancelar tasks pendentes, limpar bosses, etc.
    }

    // ---------------------------
    // Utilitários / triggers internos
    // ---------------------------

    public void completeDungeon(String dungeonId, Player player) {
        for (DungeonCompleteListener l : snapshot(completeListeners)) {
            try { l.onDungeonComplete(dungeonId, player); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonComplete: " + t.getMessage()); }
        }
    }

    public void failDungeon(String dungeonId, Player player) {
        for (DungeonFailListener l : snapshot(failListeners)) {
            try { l.onDungeonFail(dungeonId, player); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonFail: " + t.getMessage()); }
        }
    }

    public void levelUpDungeon(String dungeonId, Player player, int newLevel) {
        for (DungeonLevelUpListener l : snapshot(levelUpListeners)) {
            try { l.onDungeonLevelUp(dungeonId, player, newLevel); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonLevelUp: " + t.getMessage()); }
        }
    }

    public void mobDeath(String dungeonId, Player killer) {
        for (DungeonMobDeathListener l : snapshot(mobDeathListeners)) {
            try { l.onDungeonMobDeath(dungeonId, killer); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonMobDeath: " + t.getMessage()); }
        }
    }

    public void bossDeath(String dungeonId, Player killer) {
        for (DungeonBossDeathListener l : snapshot(bossDeathListeners)) {
            try { l.onDungeonBossDeath(dungeonId, killer); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonBossDeath: " + t.getMessage()); }
        }
    }

    public void generateLoot(String dungeonId, Player player) {
        for (DungeonLootGenerateListener l : snapshot(lootListeners)) {
            try { l.onDungeonLootGenerate(dungeonId, player); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonLootGenerate: " + t.getMessage()); }
        }

        // Exemplo: usar LootIntegrator para dropar loot no mundo do jogador (se existir)
        try {
            if (player != null) {
                lootIntegrator.dropBossLoot(player, 1); // nivel 1 por padrão; ajuste conforme necessário
            }
        } catch (Throwable t) {
            plugin.getLogger().warning("Erro ao dropar loot via LootIntegrator: " + t.getMessage());
        }
    }

    public void roomGenerated(String dungeonId, RoomData room) {
        // Armazena room no mapa de dungeons
        activeDungeons.computeIfAbsent(dungeonId, k -> Collections.synchronizedList(new ArrayList<>())).add(room);

        // Notifica listeners
        for (DungeonRoomGenerateListener l : snapshot(roomListeners)) {
            try { l.onDungeonRoomGenerate(dungeonId, room); } catch (Throwable t) { plugin.getLogger().warning("Erro em listener onDungeonRoomGenerate: " + t.getMessage()); }
        }
    }

    /**
     * Convenience: spawn a preview boss for admins.
     */
    public void forceSpawnBossPreview(Location at) {
        try {
            LordeCataclismo boss = new LordeCataclismo(plugin, lootIntegrator, 1);
            boss.spawn(at.add(0, 2, 0));
        } catch (Throwable t) {
            plugin.getLogger().warning("Erro ao spawnar boss preview: " + t.getMessage());
        }
    }

    // ---------------------------
    // Helpers
    // ---------------------------

    /**
     * Returns a safe snapshot of a synchronized list to avoid ConcurrentModificationException
     */
    private static <T> List<T> snapshot(List<T> source) {
        synchronized (source) {
            return new ArrayList<>(source);
        }
    }
}
