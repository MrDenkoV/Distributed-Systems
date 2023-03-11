#!/bin/zsh

rm -rf apache-zookeeper-3.6.1-bin/bin/Zookeeper/*
mkdir -p apache-zookeeper-3.6.1-bin/bin/Zookeeper/zk1
mkdir -p apache-zookeeper-3.6.1-bin/bin/Zookeeper/zk2
mkdir -p apache-zookeeper-3.6.1-bin/bin/Zookeeper/zk3
echo "1" >> apache-zookeeper-3.6.1-bin/bin/Zookeeper/zk1/myid
echo "2" >> apache-zookeeper-3.6.1-bin/bin/Zookeeper/zk2/myid
echo "3" >> apache-zookeeper-3.6.1-bin/bin/Zookeeper/zk3/myid

osascript -e 'tell application "Terminal"
    do script "cd Uni/rozpro/zoo/apache-zookeeper-3.6.1-bin/bin 2>/dev/null; ./zkServer.sh --config ../conf1 start"
end tell'

osascript -e 'tell application "Terminal"
    do script "cd Uni/rozpro/zoo/apache-zookeeper-3.6.1-bin/bin 2>/dev/null; ./zkServer.sh --config ../conf2 start"
end tell'

osascript -e 'tell application "Terminal"
    do script "cd Uni/rozpro/zoo/apache-zookeeper-3.6.1-bin/bin 2>/dev/null; ./zkServer.sh --config ../conf3 start"
end tell'
