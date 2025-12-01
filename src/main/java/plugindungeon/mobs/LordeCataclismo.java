package plugindungeon.mobs;

import plugindungeon.DungeonPlugin;
import plugindungeon.loot.LootIntegrator;
import org.bukkit.*;
import org.bukkit.attribute.Attribute;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Boss final hybrid (Inferno + Tempestade) - simplified but functional
 */
public class LordeCataclismo {

    private final JavaPlugin plugin;
    private final LootIntegrator lootIntegrator;
    private final int dungeonLevel;
    private LivingEntity boss;
    private Location spawnLocation;
    private volatile int phase = 1;
    private final AtomicInteger enraged = new AtomicInteger(0);
    private final List<BukkitTask> tasks = new ArrayList<>();
    private final Random random = new Random();

    public LordeCataclismo(JavaPlugin plugin, LootIntegrator lootIntegrator, int dungeonLevel) {
        this.plugin = plugin;
        this.lootIntegrator = lootIntegrator;
        this.dungeonLevel = Math.max(1, dungeonLevel);
    }

    public void spawn(Location loc) {
        this.spawnLocation = loc.clone();
        boss = (LivingEntity) loc.getWorld().spawnEntity(loc, EntityType.WITHER_SKELETON);
        boss.setCustomName("§c§lLorde Cataclismo");
        boss.setCustomNameVisible(true);

        double baseHealth = 800 + (dungeonLevel * 120);
        boss.getAttribute(Attribute.GENERIC_MAX_HEALTH).setBaseValue(baseHealth);
        boss.setHealth(baseHealth);
        boss.getAttribute(Attribute.GENERIC_ATTACK_DAMAGE).setBaseValue(18 + dungeonLevel*3);

        boss.getWorld().spawnParticle(Particle.LAVA, boss.getLocation(), 60,1,1,1);
        boss.getWorld().playSound(boss.getLocation(), Sound.ENTITY_WITHER_SPAWN, 2f, 1f);

        startBehavior();

        org.bukkit.event.HandlerList.unregisterAll(this); // ensure safe
        Bukkit.getPluginManager().registerEvents(new org.bukkit.event.Listener() {
            @org.bukkit.event.EventHandler
            public void onEntityDeath(org.bukkit.event.entity.EntityDeathEvent e) {
                if (e.getEntity().equals(boss)) onDeath(e.getEntity().getLocation());
            }
        }, plugin);
    }

    private void startBehavior() {
        // phase monitor
        tasks.add(Bukkit.getScheduler().runTaskTimer(plugin, () -> {
            if (boss == null || boss.isDead()) return;
            double perc = (boss.getHealth() / boss.getAttribute(Attribute.GENERIC_MAX_HEALTH).getBaseValue()) * 100.0;
            if (phase == 1 && perc <= 70) {
                phase = 2;
                boss.getWorld().playSound(boss.getLocation(), Sound.ENTITY_WITHER_SPAWN, 1.6f, 0.7f);
                spawnPhaseTransitionMessage("§cFase 2 — O magma desperta!");
            } else if (phase == 2 && perc <= 30) {
                phase = 3;
                enraged.incrementAndGet();
                boss.getWorld().playSound(boss.getLocation(), Sound.ENTITY_ENDER_DRAGON_GROWL, 2f, 0.6f);
                spawnPhaseTransitionMessage("§4Fase 3 — Cataclismo Total!");
            }
        }, 20L, 20L));

        // attacks
        tasks.add(Bukkit.getScheduler().runTaskTimer(plugin, () -> {
            if (boss == null || boss.isDead()) return;
            switch (phase) {
                case 1 -> { if (random.nextDouble() < 0.6) infernoAscendente(); if (random.nextDouble()<0.4) markTrovejante(); }
                case 2 -> { if (random.nextDouble() < 0.7) markTrovejante(); if (random.nextDouble()<0.6) hybridRain();}
                case 3 -> { if (random.nextDouble() < 0.8) ultimate(); if (random.nextDouble()<0.7) jumpDash(); }
            }
        }, 40L, 80L));
    }

    private void spawnPhaseTransitionMessage(String msg) {
        for (Player p : boss.getWorld().getPlayers()) {
            if (p.getLocation().distanceSquared(boss.getLocation()) < 200*200) p.sendMessage(msg);
        }
    }

    private void infernoAscendente() {
        plugin.getServer().getScheduler().runTask(plugin, () -> {
            for (Player p : boss.getWorld().getPlayers()) {
                if (p.getLocation().distance(boss.getLocation()) > 30) continue;
                Location under = p.getLocation().clone();
                under.getBlock().setType(org.bukkit.Material.LAVA);
                boss.getWorld().spawnParticle(Particle.FLAME, under, 40,1,2,1);
            }
            boss.getWorld().playSound(boss.getLocation(), Sound.ITEM_FLINTANDSTEEL_USE,1.2f,0.9f);
        });
    }

    private void markTrovejante() {
        plugin.getServer().getScheduler().runTask(plugin, () -> {
            Player target = getRandomNearPlayer(40);
            if (target == null) return;
            Location markLoc = target.getLocation().clone();
            target.sendMessage("§cVocê foi marcado pelo Lorde Cataclismo!");
            boss.getWorld().spawnParticle(Particle.SPELL_INSTANT, markLoc, 60);
            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                if (target.isDead()) return;
                boss.getWorld().strikeLightning(markLoc);
                markLoc.getBlock().setType(Material.FIRE);
                target.damage(10 + dungeonLevel*2);
            }, 60L);
        });
    }

    private void hybridRain() {
        plugin.getServer().getScheduler().runTask(plugin, () -> {
            Location center = boss.getLocation().clone();
            int strikes = 6 + dungeonLevel/2;
            for (int i = 0; i < strikes; i++) {
                Location pos = center.clone().add(random.nextInt(20)-10, 0, random.nextInt(20)-10);
                boss.getWorld().spawnParticle(Particle.FALLING_LAVA, pos.clone().add(0,10,0), 10);
                Bukkit.getScheduler().runTaskLater(plugin, () -> {
                    boss.getWorld().strikeLightning(pos);
                    pos.getBlock().setType(Material.FIRE);
                }, 20L + i*6);
            }
            boss.getWorld().playSound(center, Sound.ENTITY_WITHER_SHOOT,1.4f,0.9f);
        });
    }

    private void ultimate() {
        plugin.getServer().getScheduler().runTask(plugin, () -> {
            broadcastToNearby("§4Lorde Cataclismo prepara uma Explosão Cataclísmica!");
            Bukkit.getScheduler().runTaskLater(plugin, this::createUltimateRings, 80L);
        });
    }

    private void createUltimateRings() {
        Location center = boss.getLocation().clone();
        int maxRadius = 12 + dungeonLevel/2;
        for (int wave=1; wave<=3; wave++) {
            int radius = wave * (maxRadius/3);
            int damage = 8 + dungeonLevel*wave;
            for (int i = 0; i < 360; i += 8) {
                double rad = Math.toRadians(i);
                Location loc = center.clone().add(Math.cos(rad)*radius,0,Math.sin(rad)*radius);
                boss.getWorld().spawnParticle(Particle.EXPLOSION_NORMAL, loc, 4);
                for (Player p : boss.getWorld().getPlayers()) {
                    if (p.getLocation().distance(loc) < 2.0) p.damage(damage);
                }
            }
            try { Thread.sleep(300); } catch (InterruptedException ignored) {}
        }
        boss.getWorld().playSound(center, Sound.ENTITY_GENERIC_EXPLODE, 2f, 0.6f);
    }

    private void jumpDash() {
        plugin.getServer().getScheduler().runTask(plugin, () -> {
            Player p = getRandomNearPlayer(50);
            if (p == null) return;
            boss.teleport(p.getLocation().add(0,1,0));
            boss.getWorld().spawnParticle(Particle.CRIT, boss.getLocation(), 40);
            boss.getWorld().playSound(boss.getLocation(), Sound.ENTITY_BLAZE_SHOOT,1.2f,0.8f);
        });
    }

    private Player getRandomNearPlayer(double radius) {
        List<Player> players = new ArrayList<>();
        for (Player p : boss.getWorld().getPlayers()) if (p.getLocation().distance(boss.getLocation()) <= radius) players.add(p);
        return players.isEmpty() ? null : players.get(random.nextInt(players.size()));
    }

    private void onDeath(Location loc) {
        tasks.forEach(t -> { if (t != null) t.cancel(); });
        boss.getWorld().spawnParticle(Particle.EXPLOSION_HUGE, loc, 3);
        boss.getWorld().playSound(loc, Sound.ENTITY_WITHER_DEATH, 2f, 0.5f);

        lootIntegrator.dropBossLoot(boss, dungeonLevel);
        dropGuaranteedArtifact(loc);
        boss = null;
    }

    private void dropGuaranteedArtifact(Location loc) {
        ItemStack artifact = createArtifact();
        loc.getWorld().dropItemNaturally(loc, artifact);
    }

    private ItemStack createArtifact() {
        ItemStack item = new ItemStack(Material.NETHER_STAR);
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName("§6Núcleo do Cataclismo");
        meta.setLore(java.util.Arrays.asList("§7Um fragmento do poder do Lorde Cataclismo.","§eUsado para forjar artefatos lendários."));
        item.setItemMeta(meta);
        return item;
    }

    private void broadcastToNearby(String msg) {
        for (Player p : boss.getWorld().getPlayers()) if (p.getLocation().distanceSquared(boss.getLocation()) < 200*200) p.sendMessage(msg);
    }

    public void cleanup() {
        tasks.forEach(t -> { if (t != null) t.cancel(); });
        if (boss != null && !boss.isDead()) boss.remove();
        boss = null;
    }
}
