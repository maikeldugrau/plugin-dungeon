#!/usr/bin/env python3
"""Add isolated /aeventos admin and direct /<event> commands to aEventos."""
from pathlib import Path
import re
import sys

ROOT=Path(sys.argv[1]).resolve()
BASE="src/main/java/com/ars3ne/eventos/"
def get(path): return (ROOT/path).read_text(encoding="utf-8")
def put(path,data):
    f=ROOT/path; f.parent.mkdir(parents=True,exist_ok=True); f.write_text(data,encoding="utf-8"); print("commands:",path)
def change(src,old,new):
    if old not in src: raise RuntimeError("Missing replacement "+old[:120])
    return src.replace(old,new)

DIRECT=[
"anvil","astronauta","batataquente","battleroyale","bolao","campominado",
"corrida","fastclick","fight","frog","gladiador","hunter","killer",
"loteria","matematica","nexus","paintball","palavra","parkour","quiz",
"semaforo","sorteio","spleef","sumo","thor","votacao"
]
CHAT={"bolao","fastclick","loteria","matematica","palavra","sorteio","votacao"}
PARAMS={"loteria":"<numero>","votacao":"<opcao>","fastclick":"<linha> <posicao>"}
REGCMD="aeventos"

plugin=get("src/main/resources/plugin.yml")
idx=plugin.find("\ncommands:")
if idx<0: raise RuntimeError("plugin.yml commands section missing")
plugin=plugin[:idx]+"""
commands:
  aeventos:
    description: Administração do aEventos, sem ocupar /evento.
    usage: "/aeventos <iniciar|parar|setup|reload>"
    aliases: [ae]
"""+ "".join(
    f"  {x}:\n    description: Acesso direto ao evento {x} do aEventos.\n"
    for x in DIRECT
)
put("src/main/resources/plugin.yml",plugin)

main_path=BASE+"aEventos.java"
main=get(main_path)
main=change(main,
'this.getCommand("evento").setExecutor(new EventoCommand());',
'''this.getCommand("aeventos").setExecutor(new EventoCommand());
            com.ars3ne.eventos.commands.EventoDirectCommand direct =
                    new com.ars3ne.eventos.commands.EventoDirectCommand();
            for (String eventName : com.ars3ne.eventos.commands.EventoDirectCommand.EVENT_COMMANDS) {
                org.bukkit.command.PluginCommand directCommand = this.getCommand(eventName);
                if (directCommand != null) directCommand.setExecutor(direct);
            }''')
main=main.replace('/evento reload','/aeventos reload')
put(main_path,main)

admin_path=BASE+"commands/EventoCommand.java"
admin=get(admin_path)
admin=change(admin,
'if(cmd.getName().equalsIgnoreCase("evento")) {',
'if(cmd.getName().equalsIgnoreCase("aeventos")) {')
put(admin_path,admin)

direct_java=r'''package com.ars3ne.eventos.commands;

import com.ars3ne.eventos.aEventos;
import com.ars3ne.eventos.api.Evento;
import com.ars3ne.eventos.api.EventoChat;
import com.ars3ne.eventos.api.EventoType;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/**
 * Direct commands for MC Games aEventos.
 * /evento is not registered by this plugin, to avoid collisions with other systems.
 */
public final class EventoDirectCommand implements CommandExecutor {
    public static final Set<String> EVENT_COMMANDS = Collections.unmodifiableSet(new HashSet<>(
        Arrays.asList(
            "anvil", "astronauta", "batataquente", "battleroyale", "bolao",
            "campominado", "corrida", "fastclick", "fight", "frog",
            "gladiador", "hunter", "killer", "loteria", "matematica",
            "nexus", "paintball", "palavra", "parkour", "quiz",
            "semaforo", "sorteio", "spleef", "sumo", "thor", "votacao"
        )
    ));

    private static final Set<String> CHAT_COMMANDS = Collections.unmodifiableSet(new HashSet<>(
        Arrays.asList("bolao", "fastclick", "loteria", "matematica", "palavra", "sorteio", "votacao")
    ));

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        String requested = command.getName().toLowerCase(Locale.ROOT);
        if (!EVENT_COMMANDS.contains(requested)) return false;
        if (!(sender instanceof Player player)) {
            sender.sendMessage("§c[Eventos] Este comando deve ser executado por um jogador.");
            return true;
        }

        if (CHAT_COMMANDS.contains(requested)) {
            EventoChat chat = aEventos.getEventoChatManager().getEvento();
            if (chat == null || !isNamedEvent(chat.getConfig(), requested)) {
                player.sendMessage("§e[Eventos] Não há um evento de " + requested + " acontecendo agora.");
                return true;
            }
            if (!player.hasPermission(chat.getPermission())) {
                player.sendMessage("§c[Eventos] Você não tem permissão para participar.");
                return true;
            }
            if ("matematica".equals(requested) || "palavra".equals(requested) || "sorteio".equals(requested)) {
                player.sendMessage("§e[Eventos] Responda no chat para participar deste evento.");
                return true;
            }
            int required = "fastclick".equals(requested) ? 2 :
                    ("loteria".equals(requested) || "votacao".equals(requested)) ? 1 : 0;
            if (args.length < required) {
                String usage = "fastclick".equals(requested) ? "/fastclick <linha> <posicao>" :
                        "loteria".equals(requested) ? "/loteria <numero>" : "/votacao <opcao>";
                player.sendMessage("§e[Eventos] Uso correto: " + usage);
                return true;
            }
            chat.parseCommand(player, args);
            return true;
        }

        Evento event = aEventos.getEventoManager().getEvento();
        if (event == null || !isNamedEvent(event.getConfig(), requested)) {
            player.sendMessage("§e[Eventos] Não há um evento de " + requested + " acontecendo agora.");
            return true;
        }
        if (args.length > 0) {
            String subcommand = args[0].toLowerCase(Locale.ROOT);
            if (!subcommand.equals("sair") && !subcommand.equals("assistir") &&
                    !subcommand.equals("camarote")) {
                player.sendMessage("§e[Eventos] Uso: /" + requested + " [sair|assistir]");
                return true;
            }
        }
        org.bukkit.command.PluginCommand admin = aEventos.getInstance().getCommand("aeventos");
        if (admin == null) {
            player.sendMessage("§c[Eventos] O sistema de eventos não está configurado corretamente.");
            return true;
        }
        return new EventoCommand().onCommand(player, admin, requested, args);
    }

    private static boolean isNamedEvent(YamlConfiguration config, String name) {
        if (config == null) return false;
        String filename = config.getString("filename", "");
        if (filename.endsWith(".yml")) filename = filename.substring(0, filename.length()-4);
        if (name.equalsIgnoreCase(filename)) return true;

        // Also allow a type-level command when the active event has a custom file name.
        String type = config.getString("Evento.Type", "");
        return name.equalsIgnoreCase(type);
    }
}
'''
put(BASE+"commands/EventoDirectCommand.java",direct_java)

# Keep the allowed commands in config synced, otherwise the in-game listener
# cancels /parkour sair, /spleef sair etc. while the player is in the arena.
config_path="src/main/resources/config.yml"
cfg=get(config_path)
cfg=change(cfg,'  - "/evento"','  - "/aeventos"'+ "".join('\n  - "/'+x+'"' for x in DIRECT))
cfg=cfg.replace('/evento', '/aeventos')  # default admin message templates
put(config_path,cfg)

# Event announcements should instruct players to use their matching command,
# not the old /evento command belonging to the other event system.
for path in (ROOT/"src/main/resources/eventos").glob("*.yml"):
    text=path.read_text(encoding="utf-8")
    ev_name=path.stem
    text=re.sub(r'/evento(?![a-zA-Z0-9_])', '/'+ev_name, text)
    # Setup instructions remain admin-level /aeventos setup.
    text=text.replace('/'+ev_name+' setup ', '/aeventos setup ')
    text=text.replace('/'+ev_name+' iniciar ', '/aeventos iniciar ')
    path.write_text(text, encoding="utf-8")

with (ROOT/"MCGAMES-26.2-PORT.md").open("a", encoding="utf-8") as f:
    f.write("""\n## MC Games direct commands
- /evento is NOT claimed; it belongs to the existing MC Games event system.
- /aeventos, /ae: administration commands (e.g. /aeventos iniciar loteria).
- /loteria 7: make a lottery guess; /votacao 1: vote.
- /parkour, /spleef, /sumo, etc: join only their matching active event.
- /parkour sair, /parkour assistir: leave/spectate.
- /aeventos:loteria: explicit namespace fallback if another plugin claims /loteria.
- Custom event files still work from /aeventos, but custom player shortcuts require
  adding their name to plugin.yml and the direct command registry then rebuilding.
- Existing /evento in the MC Games system is untouched.
""")
print("Standalone event commands installed")
