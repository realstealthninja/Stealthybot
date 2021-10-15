#!/bin/bash


if [ -d storage/Stealthybot ];
then

    cd storage/Stealthybot

    python main.py

    echo "ran python main.py"
else
    python main.py;
fi
