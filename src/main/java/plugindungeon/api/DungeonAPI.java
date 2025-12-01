package plugindungeon.api;

import plugindungeon.api.listeners.*;

public interface DungeonAPI {

    void registerDungeonStartListener(DungeonStartListener listener);
    void registerDungeonCompleteListener(DungeonCompleteListener listener);
    void registerDungeonFailListener(DungeonFailListener listener);
    void registerDungeonLevelUpListener(DungeonLevelUpListener listener);

    void registerDungeonMobDeathListener(DungeonMobDeathListener listener);
    void registerDungeonBossDeathListener(DungeonBossDeathListener listener);
    void registerDungeonLootGenerateListener(DungeonLootGenerateListener listener);
    void registerDungeonRoomGenerateListener(DungeonRoomGenerateListener listener);

    void unregisterAllListeners(Object pluginInstance);

    boolean startDungeon(String dungeonId, String playerName);
}
