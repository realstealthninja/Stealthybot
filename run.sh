#!/bin/bash

runstealthybotpy() {
    cd storage/Stealthybot

    python main.py

    echo "ran python main.py"
}

runlavalink(){
    cd storage/Stealthybot

    java -jar Lavalink.jar

    echo "ran lava link"
}

