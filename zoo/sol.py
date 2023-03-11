import sys
import os
import subprocess as sps
from kazoo.client import KazooClient, KazooState
from kazoo.exceptions import NoNodeException


app=None
hosts = ['localhost:2185', 'localhost:2183','localhost:2184']
zk = KazooClient(hosts=','.join(hosts))
paths = set()


def count_kids(zk=zk, cur='/z'):
    return sum([count_kids(zk, cur+'/'+kid) for kid in zk.get_children(cur)]) + len(zk.get_children(cur))

def child_watcher(kids, event, zk=zk, paths=paths):
    if event is not None and event.type=='CHILD':
        print(f"Znode /z has {count_kids()} children")
        path=event.path
        for kid in kids:
            if path+'/'+kid not in paths:
                zk.ChildrenWatch(path+'/'+kid, child_watcher,send_event=True)
                paths |= {path+'/'+kid}


@zk.DataWatch('/z')
def watcher(data,stats):
    if stats is None:
        kill()
    else:
        start()
        zk.ChildrenWatch('/z', child_watcher,send_event=True)


def print_tree(zk=zk, cur='/z', ind=0):
    zk.get_children(cur)
    print(f"{'   '*ind}-{cur}")
    for child in zk.get_children(cur):
        print_tree(zk, cur+'/'+child, ind+1)


def start(args=sys.argv[1:]):
    global app
    if app is None or app.poll() is not None:
        print("Starting app")
        app = sps.Popen(args)


def kill(args=sys.argv[1:]):
    global app
    if app is not None:
        print("Killing app")
        app.kill()


zk.start()
print("Watching /z znode and it's children\nquit to exit, tree to display the file structure")
while(True):
    inp = input()
    if inp=='quit':
        kill()
        exit()
    elif inp=='tree':
        try:
            print_tree()
        except NoNodeException:
            print("No znode /z")
