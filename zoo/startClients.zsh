#!/bin/zsh

osascript -e 'tell application "Terminal"
    do script "cd Uni/rozpro/zoo/apache-zookeeper-3.6.1-bin/bin; ./zkCli.sh -server localhost:2185"
end tell'

osascript -e 'tell application "Terminal"
    do script "cd Uni/rozpro/zoo/apache-zookeeper-3.6.1-bin/bin; ./zkCli.sh -server localhost:2183"
end tell'

osascript -e 'tell application "Terminal"
    do script "cd Uni/rozpro/zoo/apache-zookeeper-3.6.1-bin/bin; ./zkCli.sh -server localhost:2184"
end tell'
