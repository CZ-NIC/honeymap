config =
  markersMaxVisible: 150
  colors:
    src: { stroke: 'darkred', fill: 'red' }
    dst: { stroke: '#383F47', fill: '#32CD32' }
    scale: [ '#C8EEFF', '#0071A4' ]

jQuery(document).ready ->
  log = new Log(config)
  honeymap = new Honeymap(config)

  jQuery(window).resize ->
    honeymap.fitSize()
    log.fitSize()

  log.add "<b>Welcome to HoneyMap. This is a BETA version! Bug reports welcome :-)</b>"
  log.add "Note that map display only sensors of <a href=\"https://www.nic.cz/\" target=\"_blank\">CZ.NIC</a> honeypots. You can download weekly <a href=\"https://devpub.labs.nic.cz/honey_stats/\" target=\"_blank\">honeypot data</a>."
  log.add ""
  log.add "<b>Vítejte na HoneyMap. Toto je BETA verze! Hlášení chyb a návrhy k vylepšení jsou vítány :-)</b>"
  log.add "Mapa zobrazuje pouze senzory honeypotů provozovaných sdružením <a href=\"https://www.nic.cz/\" target=\"_blank\">CZ.NIC</a>. Můžete si stáhnout <a href=\"https://devpub.labs.nic.cz/honey_stats/\" target=\"_blank\">týdenní data</a>."
  log.add ""

  new Feed(honeymap, log, "geoloc.events")
