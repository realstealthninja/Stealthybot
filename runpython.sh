#!/bin/bash


if [ -d storage/Stealthybot];
then


    python main.py

    echo "ran python main.py"
else
    python main.py;
fi
