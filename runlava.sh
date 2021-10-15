if [ -d storage/Stealthybot ];
then

    cd storage/Stealthybot

    java -jar Lavalink.jar

    echo "ran python main.py"
else
    java -jar Lavalink.jar;
    
fi
