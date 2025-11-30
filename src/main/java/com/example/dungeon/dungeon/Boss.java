package com.example.dungeon.dungeon;

import org.bukkit.Location;

public class Miniboss {
    private final String name;
    private final Location location;

    public Miniboss(String name, Location location) {
        this.name = name;
        this.location = location;
    }

    public String getName() { return name; }
    public Location getLocation() { return location; }
}

public class Boss {
    private final String name;
    private final Location location;

    public Boss(String name, Location location) {
        this.name = name;
        this.location = location;
    }

    public String getName() { return name; }
    public Location getLocation() { return location; }
}

