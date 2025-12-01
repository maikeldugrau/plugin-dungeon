package plugindungeon.core;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import plugindungeon.api.DungeonAPI;
import plugindungeon.api.listeners.*;

import java.util.*;

public class DungeonManager implements DungeonAPI {

    // ============================================================
    // LISTENERS GERENCIADOS POR PLUGIN
    // ============================================================

    private final Map<Object, List<Object>> pluginListeners = new HashMap<>();

    private final List<DungeonStartListener> startListeners = new ArrayList<>();
    private final List<DungeonCompleteListener> completeListeners = new ArrayList<>();
    private final List<DungeonFailListener> failListeners = new ArrayList<>();
    private final List<DungeonLevelUpListener> levelUpListeners = new ArrayList<>();

    private final List<DungeonMobDeathListener> mobDeathListeners = new ArrayList<>();
    private final List<DungeonBossDeathListener> bossDeathListeners = new ArrayList<>();
    private final List<DungeonLootGenerateListener> lootListeners = new ArrayList<>();
    private final List<DungeonRoomGenerateListener> roomListeners = new ArrayList<>();


    // ============================================================
    // REGISTRO DE LISTENERS
    // ============================================================

    private void storeListener(Object plugin, Object listener) {
        pluginListeners.computeIfAbsent(plugin, k -> new ArrayList<>()).add(listener);
    }

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


    // ============================================================
    // DESREGISTRO POR PLUGIN
    // ============================================================

    @Override
    public void unregisterAllListeners(Object pluginInstance) {

        List<Object> list = pluginListeners.remove(pluginInstance);

        if (list == null) return;

        startListeners.removeIf(list::contains);
        completeListeners.removeIf(list::contains);
        failListeners.removeIf(list::contains);
        levelUpListeners.removeIf(list::contains);

        mobDeathListeners.removeIf(list::contains);
        bossDeathListeners.removeIf(list::contains);
        lootListeners.removeIf(list::contains);
        roomListeners.removeIf(list::contains);
    }


    // ============================================================
    // IMPLEMENTAÇÃO DO MÉTODO PRINCIPAL DO API
    // ============================================================

    @Override
    public boolean startDungeon(String dungeonId, String playerName) {

        Player player = Bukkit.getPlayer(playerName);
        if (player == null) {
            Bukkit.getLogger().warning("[DungeonPlugin] Jogador não encontrado: " + playerName);
            return false;
        }

        player.sendMessage("§aIniciando dungeon §f" + dungeonId);

        for (DungeonStartListener listener : startListeners) {
            listener.onDungeonStart(dungeonId, player);
        }

        return true;
    }


    // ============================================================
    // DISPARADORES USADOS INTERNAMENTE PELO PLUGIN
    // ============================================================

    public void completeDungeon(String dungeonId, Player player) {
        for (DungeonCompleteListener listener : completeListeners) {
            listener.onDungeonComplete(dungeonId, player);
        }
    }

    public void failDungeon(String dungeonId, Player player) {
        for (DungeonFailListener listener : failListeners) {
            listener.onDungeonFail(dungeonId, player);
        }
    }

    public void levelUpDungeon(String dungeonId, Player player, int newLevel) {
        for (DungeonLevelUpListener listener : levelUpListeners) {
            listener.onDungeonLevelUp(dungeonId, player, newLevel);
        }
    }

    public void mobDeath(String dungeonId, Player killer) {
        for (DungeonMobDeathListener listener : mobDeathListeners) {
            listener.onDungeonMobDeath(dungeonId, killer);
        }
    }

    public void bossDeath(String dungeonId, Player killer) {
        for (DungeonBossDeathListener listener : bossDeathListeners) {
            listener.onDungeonBossDeath(dungeonId, killer);
        }
    }

    public void generateLoot(String dungeonId, Player player) {
        for (DungeonLootGenerateListener listener : lootListeners) {
            listener.onDungeonLootGenerate(dungeonId, player);
        }
    }

    public void roomGenerated(String dungeonId, int roomNumber) {
        for (DungeonRoomGenerateListener listener : roomListeners) {
            listener.onDungeonRoomGenerate(dungeonId, roomNumber);
        }
    }
}
