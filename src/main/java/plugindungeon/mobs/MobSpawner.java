package plugindungeon.mobs;

import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.attribute.Attribute;
import org.bukkit.entity.Zombie;

import java.util.Random;

public class MobSpawner {

    private static final Random r = new Random();

    public static void spawnRoomMobs(Location center, int difficulty) {
        World w = center.getWorld();
        int count = 2 + r.nextInt(2 + difficulty);
        for (int i = 0; i < count; i++) {
            Location spawn = center.clone().add(r.nextInt(6)-3, 1, r.nextInt(6)-3);
            Zombie z = (Zombie) w.spawn(spawn, org.bukkit.entity.Zombie.class);
            z.getAttribute(Attribute.GENERIC_MAX_HEALTH).setBaseValue(20 + difficulty*5);
            z.setHealth(20 + difficulty*5);
        }
    }
}
