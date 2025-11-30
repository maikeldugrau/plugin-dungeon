package com.example.dungeon.loot;

import org.bukkit.Material;
import org.bukkit.inventory.ItemStack;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class LootManager {

    private final Random random = new Random();

    public ItemStack generateLoot(int dungeonLevel) {
        // Exemplo simples: aumenta chance de itens melhores por nível
        int chance = random.nextInt(100);
        if(chance < 50 + dungeonLevel*5) {
            return new ItemStack(Material.DIAMOND_SWORD);
        } else if(chance < 80) {
            return new ItemStack(Material.IRON_SWORD);
        } else {
            return new ItemStack(Material.STONE_SWORD);
        }
    }

    public List<ItemStack> generateLootForRoom(int dungeonLevel) {
        List<ItemStack> loot = new ArrayList<>();
        int count = 1 + random.nextInt(3);
        for(int i = 0; i < count; i++) {
            loot.add(generateLoot(dungeonLevel));
        }
        return loot;
    }
}

