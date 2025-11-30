package com.example.dungeon.dungeon;

import org.bukkit.Location;

public class Room {

    private final String name;
    private final Location location;
    private Miniboss miniboss;
    private Boss boss;

    public Room(String name, Location location) {
        this.name = name;
        this.location = location;
    }

    public String getName() { return name; }
    public Location getLocation() { return location; }

    public Miniboss getMiniboss() { return miniboss; }
    public void setMiniboss(Miniboss miniboss) { this.miniboss = miniboss; }

    public Boss getBoss() { return boss; }
    public void setBoss(Boss boss) { this.boss = boss; }
}

