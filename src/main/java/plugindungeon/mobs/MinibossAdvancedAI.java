package plugindungeon.mobs;

import org.bukkit.Location;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.attribute.Attribute;

public class MinibossAdvancedAI {

    private final LivingEntity entity;

    public MinibossAdvancedAI(Location spawn, String name, int level) {
        this.entity = (LivingEntity) spawn.getWorld().spawnEntity(spawn, EntityType.STRAY);
        this.entity.setCustomName(name);
        this.entity.setCustomNameVisible(true);
        this.entity.getAttribute(Attribute.GENERIC_MAX_HEALTH).setBaseValue(50 + level*10);
        this.entity.setHealth(50 + level*10);
        // Add simple behavior: periodic leap or speed
        spawn.getWorld().spawnParticle(org.bukkit.Particle.SMOKE_NORMAL, spawn, 20);
    }

    public LivingEntity getEntity() { return entity; }
}
