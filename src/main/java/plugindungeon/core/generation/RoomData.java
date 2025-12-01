package plugindungeon.core.generation;

import org.bukkit.Location;

public class RoomData {
    public final String id;
    public final RoomType type;
    public final RoomTheme theme;
    public final Location origin;
    public final int width, height, depth;

    public RoomData(String id, RoomType type, RoomTheme theme, Location origin, int width, int height, int depth) {
        this.id = id;
        this.type = type;
        this.theme = theme;
        this.origin = origin;
        this.width = width;
        this.height = height;
        this.depth = depth;
    }

    public org.bukkit.Location getCenter() {
        return origin.clone().add(width / 2.0, height / 2.0, depth / 2.0);
    }
}
