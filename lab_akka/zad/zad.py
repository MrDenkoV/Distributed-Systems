from enum import Enum
import random
import time
import pykka
import traceback as tb
import os
import sqlite3

QUERY_DATABASE_UPDATE = True
SATELLITE_DATABASE_UPDATE = not QUERY_DATABASE_UPDATE

class satellite_api:
    class status(Enum):
        OK = 1
        BATTERY_LOW = 2
        PROPULSION_ERROR = 3
        NAVIGATION_ERROR = 4

    @staticmethod
    def get_status(index):
        try:
            time.sleep(0.1+random.randint(0,400)/1000)
        except:
            print(f"{id} had an error")
        p = random.random()
        if p <= 0.8:
            return satellite_api.status.OK
        elif p <= 0.9:
            return satellite_api.status.BATTERY_LOW
        elif p <= 0.95:
            return satellite_api.status.NAVIGATION_ERROR
        else:
            return satellite_api.status.PROPULSION_ERROR


class satellite(pykka.ThreadingActor):
    def __init__(self, ix, worker):
        super().__init__()
        self.ix = ix
        self.worker = worker

    def on_receive(self, msg):
        # print(self.worker.actor_ref.__dict__)
        self.worker.tell({'from':'satellite','status':satellite_api.get_status(self.ix)})

    def on_failure(self, exception_type, exception_value, traceback):
        print(f"Satellite {self.ix} failed")
        print(exception_type)
        print(exception_value)
        tb.print_tb(traceback)
        worker.proxy().restart()

    def on_stop(self):
        # print(f"Satellite {self.ix} stopped")
        pass


class worker(pykka.ThreadingActor):
    def __init__(self, ix, dispatcher, db):
        super().__init__()
        self.resulters = set()
        self.pokers = dict()
        self.sat = satellite.start(ix, self.actor_ref)
        self.ix = ix
        self.runnning = False
        self.dispatcher = dispatcher
        self.db=db

    def on_receive(self, msg):
        if msg['from']=='satellite':
            status=msg['status']
            for resulter in self.resulters:
                resulter.tell({'status':status, 'ix':self.ix})
            if SATELLITE_DATABASE_UPDATE and status != satellite_api.status.OK and len(self.resulters)>0:
                self.db.tell({'type':'update', 'id':self.ix})
            self.resulters = set()
            self.pokers = dict()
            self.runnning = False
        elif msg['from']=='poker':
            if msg['type']=='ask':
                self.resulters |= {msg['resulter']}
                self.pokers[msg['resulter']]=msg['poker']
                if not self.runnning:
                    self.sat.tell(None)
                    self.runnning=True
            elif msg['type']=='timeout' and msg['resulter'] in self.resulters:
                resulter = msg['resulter']
                resulter.tell({'status':'timeout'})
                self.resulters -= {resulter}
                del self.pokers[resulter]
            elif msg['type']=='fail' and msg['resulter'] in self.resulters:
                self.resulters -= {msg['resulter']}
                del self.pokers[msg['resulter']]

    def on_failure(self, exception_type, exception_value, traceback):
        print(f"Worker {self.ix} failed")
        print(exception_type)
        print(exception_value)
        tb.print_tb(traceback)
        self.sat.stop()
        for resulter in self.resulters:
            self.pokers[resulter].stop()
            resulter.stop()
        self.dispatcher.proxy().restart(self.ix)

    def on_stop(self):
        # print(f"Worker {self.ix} stopped")
        for resulter in self.resulters:
            self.pokers[resulter].stop()
            resulter.stop()
        self.sat.stop()

    def restart(self):
        print(f"Restarting satellite {self.ix}")
        self.sat = satellite.start(ix, self.actor_ref)
    

class poker(pykka.ThreadingActor):
    def __init__(self, workers, timeout, resulter):
        super().__init__()
        self.workers=workers
        self.timeout=timeout
        self.resulter=resulter
    
    def on_start(self):
        for worker in self.workers:
            worker.tell({'from':'poker','type':'ask', 'resulter':self.resulter, 'poker':self.actor_ref})
        time.sleep(self.timeout/1000)
        for worker in self.workers:
            worker.tell({'from':'poker','type':'timeout','resulter':self.resulter, 'poker': self.actor_ref})
        self.stop(block=False)

    def on_failure(self, exception_type, exception_value, traceback):
        print("Poker failed")
        for worker in self.workers:
            worker.tell({'from':'poker', 'type':'fail', 'poker': self.actor_ref})
        resulter.stop()


class resulter(pykka.ThreadingActor):
    def __init__(self, station, qid, sats, db):
        super().__init__()
        self.station=station
        self.db=db
        self.qid=qid
        self.idmap=dict()
        self.sats=sats
        self.done=0
        self.timeouts=0

    def on_receive(self,msg):
        if msg['status']=='timeout':
            self.timeouts+=1
        elif msg['status']!=satellite_api.status.OK:
            self.idmap[msg['ix']]=msg['status']
            if QUERY_DATABASE_UPDATE:
                self.db.tell({'type':'update', 'id':msg['ix']})
        self.done += 1
        if self.done==self.sats:
            self.station.tell({'from':'resulter', 'type':'ok', 'query_id':self.qid, 'id_map': self.idmap, '%':round(self.timeouts/self.sats*100,2)})
            self.stop()

    def on_failure(self, exception_type, exception_value, traceback):
        print("Resulter failed - rip")
        print(exception_type)
        print(exception_value)
        tb.print_tb(traceback)
        self.station.tell({'from':'resulter', 'type':'fail', 'query_id': self.qid})


class databaser(pykka.ThreadingActor):
    def __init__(self, name, dispatcher):
        super().__init__()
        if os.path.exists(name):
            os.remove(name)
        self.name=name
        self.dispatcher=dispatcher

    def on_start(self):
        con=sqlite3.connect(self.name)
        cur=con.cursor()
        try:
            res=cur.execute('''CREATE TABLE errors (id integer, count integer)''')
        except sqlite3.Error as er:
            print(er.args)
            print(er.__class__)
        con.commit()
        for i in range(100, 200):
            cur.execute('''INSERT INTO errors VALUES ({}, 0)'''.format(i))
        con.commit()
        con.close()
        print('db initialised')

    def on_receive(self, msg):
        con=sqlite3.connect(self.name)
        cur=con.cursor()
        if msg['type']=='update':
            current = cur.execute('''SELECT count from errors WHERE id={}'''.format(msg['id'])).fetchone()[0]
            cur.execute('''UPDATE errors SET id = {}, count = {} WHERE id = {}'''.format(msg['id'],current+1,msg['id']))
            con.commit()
        elif msg['type']=='get':
            current = cur.execute('''SELECT count from errors WHERE id={}'''.format(msg['id'])).fetchone()[0]
            msg['station'].tell({'from':'database', 'id':msg['id'], 'errors':current})
        con.close()

    def on_stop(self):
        print("Database stopped")
    
    def on_failure(self, exception_type, exception_value, traceback):
        print("Database failed")
        print(exception_type)
        print(exception_value)
        tb.print_tb(traceback)
        self.dispatcher.proxy().restartdb()


class dispatcher(pykka.ThreadingActor):
    def __init__(self, name='.database123.db'):
        super().__init__()
        self.db=databaser.start(name, self.actor_ref)

    def on_start(self):
        self.workers = [worker.start(ix, self, self.db) for ix in range(100,200)]

    def on_receive(self, msg):
        if msg['type']=='query':
            resu = resulter.start(msg['station'], msg['query_id'], msg['range'], self.db)
            poker.start(self.workers[msg['first_sat_id']-100:msg['first_sat_id']-100+msg['range']], msg['timeout'], resu)
        elif msg['type']=='result':
            print(f"Station: {msg['name']}, time: {msg['time']}, errors: {len(msg['id_map'])}")
            print('\n'.join([f"id: {id}, error: {error}" for id, error in msg['id_map'].items()]))
        elif msg['type']=='database':
            self.db.tell({'type':'get', 'id':msg['id'], 'station':msg['station']})

    def on_stop(self):
        print("Dispatcher stopped")
        for worker in self.workers:
            worker.stop()
        print("Workers stopped")
        self.db.stop()
    
    def on_failure(self, exception_type, exception_value, traceback):
        print("Dispatcher failed")
        print(exception_type)
        print(exception_value)
        tb.print_tb(traceback)
        for worker in self.workers:
            worker.stop()
        self.db.stop()
    
    def restart(self, ix):
        self.workers[ix] = worker.start(ix, self)

    def restartdb(self):
        self.db=databaser.start(db, self.actor_ref)


class monitoring_station(pykka.ThreadingActor):
    def __init__(self, name, dispatcher):
        super().__init__()
        self.name=name
        self.dispatcher=dispatcher
        self.ix=0
        self.times = dict()
    
    def on_receive(self, msg):
        if msg['from']=='user':
            if msg['type']=='query':
                self.dispatcher.tell({'type':'query', 'station':self.actor_ref, 'query_id':self.ix, 'first_sat_id':msg['first_sat_id'], 'range':msg['range'], 'timeout':msg['timeout']})
                self.times[self.ix]=time.time()
                self.ix += 1
            elif msg['type']=='database':
                self.dispatcher.tell({'type':'database', 'station':self.actor_ref, 'id':msg['id']})
        elif msg['from']=='resulter' and msg['type']=='ok':
            tim=round((time.time()-self.times[msg['query_id']])*1000)
            del self.times[msg['query_id']]
            self.dispatcher.tell({'type':'result','name':self.name,'time':tim,'id_map':msg['id_map']})
        elif msg['from']=='resulter' and msg['type']=='error':
            print(f"Query: {msg['query_id']} failed")
        elif msg['from']=='database' and msg['errors']>0:
            print(f"Database query: id = {msg['id']}, errors = {msg['errors']}")

    @staticmethod
    def query(station, first_sat_id, range, timeout):
        station.tell({'from':'user', 'type': 'query','first_sat_id':first_sat_id, 'range':range, 'timeout':timeout})

    @staticmethod
    def querydb(station, id):
        station.tell({'from':'user', 'type':'database', 'id':id}) 


def test():
    dispatch = dispatcher.start()
    monitoring_stationA = monitoring_station.start('Pierwsi', dispatch)
    monitoring_stationB = monitoring_station.start('Drudzy', dispatch)
    monitoring_stationC = monitoring_station.start('Trzeci', dispatch)
    
    for station in [monitoring_stationA, monitoring_stationB, monitoring_stationC]*2:
        monitoring_station.query(station=station, first_sat_id=random.randint(100,150), range=50, timeout=300)
    # monitoring_station.query(station=monitoring_stationA, first_sat_id=100, range=50, timeout=300)


    time.sleep(1)
    for i in range(100, 200):
        monitoring_station.querydb(monitoring_stationA, i)
    input()
    monitoring_stationA.stop()
    monitoring_stationB.stop()
    monitoring_stationC.stop()
    dispatch.stop()

test()    
