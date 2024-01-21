# Music bot
Since a lot of discord music bots are being blocked by youtube nowadays I've decided to write up a quick project that will allow anyone to host their own discord bot. This bot includes the following commands:

/play - plays a song either via name or youtube link
/nowplaying - Displays what song is currently playing
/q - displays the current music queue and their ids\
/remove # - Removes a song from the queue, replace # with the song id you want removed (Hint: Do /q before and it will display the songs in queue and their respective IDS)\
/skip - skips the current song being played\
/shuffle - shuffles the songs in the queue
/clear - Stops the music and clears the queue\
/leave - Disconnected the bot from the voice channel\
/pause - pauses the current song being played or resumes if already paused\
/resume - resumes playing the current song

# Creating your bot
To obtain a token and create a bot please watch this video
https://www.youtube.com/watch?v=PJDuI9n7rWE&t=325s
It goes over how to access the discord developer application website and create a bot which then gives you a token to use.

# Installation
To run the discord bot all you need is python 3.4 or above.\
Then run pip install all the requirments from the requirements document.\
Finally open the import discord.py file and enjoy the bot.\
Please note that you will also need to have [ffmpeg](https://ffmpeg.org/download.html) installed and make sure that the path to the bin folder is in your environment variables. 


# Token
Remember that you need to have your OWN token for this bot to work. You can input your own token all the way at the bottom of the import discord.py file.
`TOKEN = 'Copy and paste your token here'`
