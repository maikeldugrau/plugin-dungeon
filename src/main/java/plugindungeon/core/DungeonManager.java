package plugindungeon.core;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import plugindungeon.api.DungeonAPI;
import plugindungeon.api.listeners.*;

import java.util.ArrayList;
import java.util.List;

public class DungeonManager implements DungeonAPI {

    // LISTAS DE LISTENERS
    private final List<DungeonStartListener> startListeners = new ArrayList<>();
    private final List<DungeonCompleteListener> completeListeners = new ArrayList<>();
    private final List<DungeonFailListener> failListeners = new ArrayList<>();
    private final List<DungeonLevelUpListener> levelUpListeners = new ArrayList<>();

    private final List<DungeonMobDeathListener> mobDeathListeners = new ArrayList<>();
    private final List<DungeonBossDeathListener> bossDeathListeners = new ArrayList<>();
    private final List<DungeonLootGenerateListener> lootListeners = new ArrayList<>();
    private final List<DungeonRoomGenerateListener> roomListeners = new ArrayList<>();


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


    @Override
    public void unregisterAllListeners(Object pluginInstance) {
        // Remove tudo (simples)
        startListeners.clear();
        completeListeners.clear();
        failListeners.clear();
        levelUpListeners.clear();
        mobDeathListeners.clear();
        bossDeathListeners.clear();
        lootListeners.clear();
        roomListeners.clear();
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

        // Mensagem simples
        player.sendMessage("§aIniciando dungeon §f" + dungeonId);

        // Disparar evento
        for (DungeonStartListener listener : startListeners) {
            listener.onDungeonStart(dungeonId, player);
        }

        return true;
    }


    // ============================================================
    // DISPARADORES UTILIZADOS INTERNAMENTE PELO PLUGIN
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
