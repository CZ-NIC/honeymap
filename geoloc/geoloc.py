import sys
import datetime
import logging
logging.basicConfig(level=logging.CRITICAL)

import hpfeeds
from processors import *

import GeoIP

HOST = 'hpfeeds.honeycloud.net'
PORT = 20000
CHANNELS = [
#   'dionaea.connections',
    'dionaea.capture',
    'glastopf.events',
#    'beeswarm.hive',
    'kippo.sessions',
    'conpot.events',
#    'artillery',
]
GEOLOC_CHAN = 'geoloc.events'
IDENT = 'ident'
SECRET = 'secret'

PROCESSORS = {
    'glastopf.events': [glastopf_event,],
    'dionaea.capture': [dionaea_capture,],
#   'dionaea.connections': [dionaea_connections,],
    'beeswarm.hive': [beeswarm_hive,],
    'kippo.sessions': [kippo_sessions,],
    'conpot.events': [conpot_events,],
    'artillery': [artillery,],
}

def main():
    import socket
    gi = {}
    gi[socket.AF_INET] = GeoIP.open("/opt/honeymap/GeoLiteCity.dat", GeoIP.GEOIP_STANDARD)
    gi[socket.AF_INET6] = GeoIP.open("/opt/honeymap/GeoLiteCityv6.dat", GeoIP.GEOIP_STANDARD)

    try:
        hpc = hpfeeds.new(HOST, PORT, IDENT, SECRET)
    except hpfeeds.FeedException, e:
        print >>sys.stderr, 'feed exception:', e
        return 1

    print >>sys.stderr, 'connected to', hpc.brokername

    def on_message(identifier, channel, payload):
        procs = PROCESSORS.get(channel, [])
#        print ' -> {0}'.format(payload)
        p = None
        for p in procs:
            try:
                m = p(identifier, payload, gi)
            except Exception as e:
                print "Exception: " + format(e)
                print format(identifier) + " " + format(channel) + " invalid message " + format(payload)
                continue
            try: tmp = json.dumps(m, encoding="latin1")
            except: print 'DBG', m
            print ' -> {0}'.format(m)
            sys.stdout.flush()
#            print ' -> {0}'.format(tmp)
#            if m != None: hpc.publish(GEOLOC_CHAN, json.dumps(m, encoding="latin1"))
            if m != None: hpc.publish(GEOLOC_CHAN, tmp)

        if not p:
            print 'not p?'

    def on_error(payload):
        print >>sys.stderr, ' -> errormessage from server: {0}'.format(payload)
        hpc.tryconnect()

    hpc.subscribe(CHANNELS)
    try:
        hpc.run(on_message, on_error)
    except hpfeeds.FeedException, e:
        print >>sys.stderr, 'feed exception:', e
    except KeyboardInterrupt:
        pass
    except:
        import traceback
        traceback.print_exc()
    finally:
        hpc.close()
    return 0

if __name__ == '__main__':
    try: sys.exit(main())
    except KeyboardInterrupt:sys.exit(0)
