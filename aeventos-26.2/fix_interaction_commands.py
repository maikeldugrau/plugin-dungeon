#!/usr/bin/env python3
"""Fix remaining interactive event collisions with MC Games /evento and chat."""
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve()
BASE = "src/main/java/com/ars3ne/eventos/"

def edit(rel, before, after):
    p=ROOT/rel
    s=p.read_text(encoding="utf-8")
    if before not in s:
        raise RuntimeError("Missing expected source fragment in "+rel+": "+before[:150])
    p.write_text(s.replace(before, after), encoding="utf-8")
    print("fixed:",rel)

# Links in interactive chat cards MUST target our plugin explicitly.
# /fastclick could also be registered by a Skript or another plugin;
# namespaced commands remove all routing ambiguity.
edit(BASE+"eventos/chat/FastClick.java",
    'new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/evento " + i + " " + z)',
    'new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/aeventos:fastclick " + i + " " + z)')
edit(BASE+"eventos/chat/Votacao.java",
    'new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/evento " + evento_id)',
    'new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/aeventos:votacao " + evento_id)')

# Keep player chat completely untouched by default.
# Direct /matematica and /palavra commands are the supported interaction mode.
listener_path=BASE+"listeners/EventoChatListener.java"
p=ROOT/listener_path
src=p.read_text(encoding="utf-8")
src=src.replace(
    'if (aEventos.getEventoChatManager().getEvento() == null) return;',
    '''if (!aEventos.getInstance().getConfig().getBoolean("ChatAnswers.Enabled", false)) return;
        if (aEventos.getEventoChatManager().getEvento() == null) return;
        com.ars3ne.eventos.api.EventoType eventType =
                aEventos.getEventoChatManager().getEvento().getType();
        if (eventType != com.ars3ne.eventos.api.EventoType.MATEMATICA &&
                eventType != com.ars3ne.eventos.api.EventoType.PALAVRA) return;
        if (!e.getPlayer().hasPermission(aEventos.getEventoChatManager().getEvento().getPermission())) return;''',
    1
)
if 'ChatAnswers.Enabled' not in src:
    raise RuntimeError("Could not restrict legacy chat hook")
p.write_text(src,encoding="utf-8")

# The previously generated direct router told maths/word players to use chat.
# Instead, forward the answer directly to the active event.
edit(BASE+"commands/EventoDirectCommand.java",
'''            if ("matematica".equals(requested) || "palavra".equals(requested) || "sorteio".equals(requested)) {
                player.sendMessage("§e[Eventos] Responda no chat para participar deste evento.");
                return true;
            }''',
'''            if ("matematica".equals(requested) || "palavra".equals(requested)) {
                if (args.length == 0) {
                    player.sendMessage("§e[Eventos] Use /" + requested + " <resposta>.");
                    return true;
                }
                chat.parsePlayerMessage(player, String.join(" ", args));
                return true;
            }''')

# Existing installed YAML event files should not continue to advertise
# /evento (which belongs to the other system) in their messages.
path=ROOT/(BASE+"utils/EventoConfigFile.java")
src=path.read_text(encoding="utf-8")
before='''        config.set("filename", name + ".yml");

        return config;'''
after='''        config.set("filename", name + ".yml");

        // Migrate announcement text in memory, including previously existing
        // config files. Leave saved YAML and technical settings untouched.
        org.bukkit.configuration.ConfigurationSection messages = config.getConfigurationSection("Messages");
        if (messages != null) {
            for (String key : messages.getKeys(true)) {
                String path = "Messages." + key;
                if (config.isString(path)) {
                    config.set(path, rewriteEventCommand(config.getString(path), name));
                } else if (config.isList(path)) {
                    java.util.List<String> rewritten = new java.util.ArrayList<>();
                    for (String line : config.getStringList(path)) {
                        rewritten.add(rewriteEventCommand(line, name));
                    }
                    config.set(path, rewritten);
                }
            }
        }
        return config;'''
if before not in src:
    raise RuntimeError("EventConfigFile get() not found")
src=src.replace(before,after,1)
needle='''    public static boolean exists(String name) {'''
insert=r'''    private static String rewriteEventCommand(String message, String name) {
        if (message == null) return null;
        String result = message.replaceAll("(?i)/evento\\s+(?=setup\\b|iniciar\\b|parar\\b|cancelar\\b|reload\\b|forcestart\\b|kick\\b|criarconfig\\b|ajuda\\b)", "/aeventos ");
        return result.replaceAll("(?i)/evento\\b", "/" + name);
    }

'''
if needle not in src:
    raise RuntimeError("EventConfigFile exists() missing")
src=src.replace(needle,insert+needle,1)
path.write_text(src,encoding="utf-8")

# Global configuration setting: default false even for existing installs
# without this section, to avoid stealing ordinary chat messages from MC Games.
config=ROOT/"src/main/resources/config.yml"
cfg=config.read_text(encoding="utf-8")
if "ChatAnswers:" not in cfg:
    cfg += """
# Isolamento do chat com o sistema de eventos proprio do MC Games.
# false (padrao): /matematica <resposta>, /palavra <resposta>
# true: aceitar tambem respostas no chat publico para esses eventos.
ChatAnswers:
  Enabled: false
"""
config.write_text(cfg,encoding="utf-8")

readme=ROOT/"MCGAMES-26.2-PORT.md"
with readme.open("a",encoding="utf-8") as f:
    f.write("""
## Correcoes de interacao
- Os cliques do FastClick usam /aeventos:fastclick <linha> <posicao>.
- Os cliques da Votacao usam /aeventos:votacao <opcao>.
- /matematica <resposta> e /palavra <resposta> funcionam sem interceptar chat.
- Config: ChatAnswers.Enabled = false (inclusive quando a chave estiver ausente).
- Mensagens YAML antigas que ainda dizem /evento sao ajustadas em memoria
  ao carregar, sem sobrescrever configuracoes existentes.
- O plugin nunca registra o comando /evento.
""")
print("Interaction collisions fixed")
