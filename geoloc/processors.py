import json
import traceback
import datetime
import urlparse
import socket

geoloc_Prague = {}
geoloc_Prague['city'] = 'Prague'
geoloc_Prague['country_name'] = 'Czech Republic'
geoloc_Prague['country_code'] = 'CZ'
geoloc_Prague['latitude'] = 50.08330154418945
geoloc_Prague['longitude'] = 14.466699600219727
geoloc2 = geoloc_Prague

geoloc_San_Jose = {}
geoloc_San_Jose['city'] = 'San Jose'
geoloc_San_Jose['country_name'] = 'United States'
geoloc_San_Jose['country_code'] = 'US'
geoloc_San_Jose['latitude'] = 37.33940124511719
geoloc_San_Jose['longitude'] = -121.8949966430664

geoloc_Sydney = {}
geoloc_Sydney['city'] = 'Sydney'
geoloc_Sydney['country_name'] = 'Australia'
geoloc_Sydney['country_code'] = 'AU'
geoloc_Sydney['latitude'] = -33.86149978637695
geoloc_Sydney['longitude'] = 151.20550537109375

class ezdict(object):
    def __init__(self, d):
        self.d = d
    def __getattr__(self, name):
        return self.d.get(name, None)

# time string
def timestr(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# geoloc_none
def geoloc_none(t):
    if t == None: return {'latitude': None, 'longitude': None, 'city': None, 'country_name': None, 'country_code': None}
    if t['city'] != None: t['city'] = t['city'].decode('latin1')
    return t

def get_addr_family(addr):
        ainfo = socket.getaddrinfo(addr, 1, socket.AF_UNSPEC, socket.SOCK_STREAM)
        return ainfo[0][0]

def glastopf_event(identifier, payload, gi):
    if identifier != 'ident':
        print identifier + " " + 'glastopf' + " " + format(payload)
        return

    try:
        dec = ezdict(json.loads(str(payload)))
        req = ezdict(dec.request)
        sip, sport = dec.source
        tstamp = datetime.datetime.strptime(dec.time, '%Y-%m-%d %H:%M:%S')
    except:
        print 'exception processing glastopf event', repr(payload)
        traceback.print_exc()
        return

    if dec.pattern == 'unknown': return None

    a_family = get_addr_family(sip)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(sip) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(sip) )

    return {'type': 'glastopf.events', 'sensor': identifier, 'time': str(tstamp), 'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': sip, 'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code'],
'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'], 'city2': geoloc2['city'], 'country2': geoloc2['country_name'], 'countrycode2': geoloc2['country_code']}


def dionaea_capture(identifier, payload, gi):
    try:
        dec = ezdict(json.loads(str(payload)))
    except:
        print 'exception processing dionaea event'
        traceback.print_exc()
        return

    a_family = get_addr_family(dec.saddr)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(dec.saddr) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(dec.saddr) )

    if identifier == 'ident':
        if dec.daddr == '1':
            dec.daddr = 'ip1'
        elif dec.daddr == '2':
            dec.daddr = 'ip2'
        print dec.time + "," + dec.daddr + "," + dec.dport + "," + dec.saddr + "," + dec.sport + ",https://www.virustotal.com/search/?query=" + dec.md5
    else:
        print identifier + " " + 'dionaea' + " " + format(payload)
        return

#    return {'type': 'dionaea.capture', 'sensor': identifier, 'time': dec.time, 'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': dec.saddr, 'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'], 'dest': dec.daddr, 'md5': dec.md5,
    return {'type': 'dionaea.capture', 'sensor': identifier, 'time': dec.time, 'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': dec.saddr, 'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'], 'md5': dec.md5,
'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code'],
'city2': geoloc2['city'], 'country2': geoloc2['country_name'], 'countrycode2': geoloc2['country_code']}


def dionaea_connections(identifier, payload, gi):
    try:
        dec = ezdict(json.loads(str(payload)))
        tstamp = datetime.datetime.now()
    except:
        print 'exception processing dionaea event'
        traceback.print_exc()
        return

    a_family = get_addr_family(dec.remote_host)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(dec.remote_host) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(dec.remote_host) )


    return {'type': 'dionaea.connections', 'sensor': identifier, 'time': timestr(tstamp), 'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': dec.remote_host, 'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'], 'dest': dec.local_host, 'md5': dec.md5,
'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code'],
'city2': geoloc2['city'], 'country2': geoloc2['country_name'], 'countrycode2': geoloc2['country_code']}

def beeswarm_hive(identifier, payload, gi):
    try:
        dec = ezdict(json.loads(str(payload)))
        sip = dec.attacker_ip
        dip = dec.honey_ip
        tstamp = datetime.datetime.strptime(dec.timestamp, '%Y-%m-%dT%H:%M:%S.%f')
    except:
        print 'exception processing beeswarm.hive event', repr(payload)
        traceback.print_exc()
        return

    a_family = get_addr_family(sip)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(sip) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(sip) )

    return {'type': 'beeswarm.hive', 'sensor': identifier, 'time': str(tstamp),
            'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code'],
            'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'], 'city2': geoloc2['city'], 'country2': geoloc2['country_name'], 'countrycode2': geoloc2['country_code']}

def kippo_sessions(identifier, payload, gi):
    try:
        dec = ezdict(json.loads(str(payload)))
        tstamp = datetime.datetime.now()
    except:
        print 'exception processing kippo event'
        traceback.print_exc()
        return

    a_family = get_addr_family(dec.peerIP)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(dec.peerIP) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(dec.peerIP) )

#    print dec.time + "," + dec.peerIP + "," + dec.hostPort + "," + dec.hostIP + "," + dec.peerPort, + "," + dec.permalink
    geoloc2 = {}
    if identifier == 'ident':
        dec.hostIP = 'ip3'
        geoloc2 = geoloc_Prague
    elif identifier == 'vps_ident':
        if dec.hostIP == 'vps1':
            geoloc2 = geoloc_San_Jose
        elif dec.hostIP == 'vps2':
            geoloc2 = geoloc_Sydney
        else:
            if a_family == socket.AF_INET:
                geoloc2 = geoloc_none( gi[a_family].record_by_addr(dec.hostIP) )
            elif a_family == socket.AF_INET6:
                geoloc2 = geoloc_none( gi[a_family].record_by_addr_v6(dec.hostIP) )
    else:
        print identifier + " " + 'kippo' + " " + format(payload)
        return

    if dec.shasum:
        print "kippo.shasum " + format(payload)

    return {'type': 'kippo.sessions', 'sensor': identifier, 'time': timestr(tstamp),
'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': dec.peerIP,
#'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'], 'dest': dec.hostIP,
'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'],
'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code'],
'city2': geoloc2['city'], 'country2': geoloc2['country_name'], 'countrycode2': geoloc2['country_code']}

def conpot_events(identifier, payload, gi):
    if identifier != 'ident' and identifier != 'vps_ident':
        print identifier + " " + 'conpot' + " " + format(payload)
        return

    try:
        dec = ezdict(json.loads(str(payload)))
        remote = dec.remote[0]

        # http asks locally for snmp with remote ip = "127.0.0.1"
        if remote == "127.0.0.1":
            return

        tstamp = datetime.datetime.strptime(dec.timestamp, '%Y-%m-%dT%H:%M:%S.%f')
    except:
        print 'exception processing conpot event'
        traceback.print_exc()
        return

    a_family = get_addr_family(remote)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(remote) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(remote) )

    geoloc2 = {}
    if identifier == 'ident':
        geoloc2 = geoloc_Prague
    elif identifier == 'vps_ident':
        if dec.public_ip == 'vps1':
            geoloc2 = geoloc_San_Jose
        elif dec.public_ip == 'vps2':
            geoloc2 = geoloc_Sydney
        else:
            if a_family == socket.AF_INET:
                geoloc2 = geoloc_none( gi[a_family].record_by_addr(dec.public_ip) )
            elif a_family == socket.AF_INET6:
                geoloc2 = geoloc_none( gi[a_family].record_by_addr_v6(dec.public_ip) )

    type = 'conpot.events-' + dec.data_type

    message = {'type': type, 'sensor': identifier, 'time': timestr(tstamp),
'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': remote,
'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code']}

#    if dec.public_ip:
    message['latitude2'] = geoloc2['latitude']
    message['longitude2'] = geoloc2['longitude']
    message['city2'] = geoloc2['city']
    message['country2'] = geoloc2['country_name']
    message['countrycode2'] = geoloc2['country_code']

    return message

def artillery(identifier, payload, gi):
    try:
        dec = ezdict(json.loads(str(payload)))
        tstamp = datetime.datetime.now()
    except:
        print 'exception processing artillery event'
        traceback.print_exc()
        return

    a_family = get_addr_family(dec.remote_host)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(dec.remote_host) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(dec.remote_host) )

    return {'type': 'artillery', 'sensor': identifier, 'time': timestr(tstamp),
'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': dec.remote_host,
'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'], 'dest': dec.local_host,
'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code'],
'city2': geoloc2['city'], 'country2': geoloc2['country_name'], 'countrycode2': geoloc2['country_code']}


def turris(identifier, payload, gi):
    if identifier != 'turris_ident':
        print identifier + ' turris ' + format(payload)
        return

    try:
        dec = ezdict(json.loads(str(payload)))
    except:
        print 'exception processing turris event'
        traceback.print_exc()
        return

    remote = dec.remote

    a_family = get_addr_family(remote)
    if a_family == socket.AF_INET:
        geoloc = geoloc_none( gi[a_family].record_by_addr(remote) )
    elif a_family == socket.AF_INET6:
        geoloc = geoloc_none( gi[a_family].record_by_addr_v6(remote) )

    tstamp = datetime.datetime.now()

    message = {'type': 'turris', 'sensor': identifier, 'time': timestr(tstamp),
'latitude': geoloc['latitude'], 'longitude': geoloc['longitude'], 'source': remote,
'city': geoloc['city'], 'country': geoloc['country_name'], 'countrycode': geoloc['country_code'],
'latitude2': geoloc2['latitude'], 'longitude2': geoloc2['longitude'],
'city2': geoloc2['city'], 'country2': geoloc2['country_name'], 'countrycode2': geoloc2['country_code']}

    return message
