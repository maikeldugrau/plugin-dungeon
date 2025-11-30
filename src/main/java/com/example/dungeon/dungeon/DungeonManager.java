package com.example.dungeon.dungeon;

import com.example.dungeon.loot.LootManager;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;

import java.util.ArrayList;
import java.util.List;

public class DungeonManager {

    private final List<Room> rooms = new ArrayList<>();
    private final LootManager lootManager = new LootManager();

    public void generateDungeon() {
        // Para exemplo, cria 5 salas simples
        World world = Bukkit.getWorlds().get(0);
        Location start = new Location(world, 100, 64, 100);

        for(int i = 0; i < 5; i++) {
            Room room = new Room("Sala " + (i+1), start.clone().add(i*10, 0, 0));
            rooms.add(room);
        }
    }

    public Miniboss spawnMiniboss() {
        // Gera miniboss simples na primeira sala
        Room room = rooms.get(0);
        Miniboss miniboss = new Miniboss("Miniboss Alpha", room.getLocation());
        room.setMiniboss(miniboss);
        return miniboss;
    }

    public Boss spawnBoss() {
        // Boss final na última sala
        Room room = rooms.get(rooms.size() - 1);
        Boss boss = new Boss("Boss Final", room.getLocation());
        room.setBoss(boss);
        return boss;
    }

    public List<Room> getRooms() {
        return rooms;
    }

    public LootManager getLootManager() {
        return lootManager;
    }
}

