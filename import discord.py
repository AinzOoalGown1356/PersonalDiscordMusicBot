import discord
import random
import asyncio
import yt_dlp
import queue
from queue import Queue
from discord.ext import commands


intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'default_search': 'auto',
    'noplaylist': True,
    'verbose': True
}

song_queue = []
current_playing_title = ""
current_playing_url = ""

ytdl = yt_dlp.YoutubeDL(ydl_opts)
bot.is_playing = False

@bot.command()
async def join(ctx): #We use async commands for all our commands so that other parts of the code/commands can be executed too without stopping the whole bot
    voice_channel = ctx.author.voice.channel #Retrive what VC the user of the command is sitting in
    voice_client = ctx.voice_client #Checks for previous voice client association

    if voice_client is None: #If there is no existing voice client then await joining the current VC of the user
        await voice_channel.connect() #By using await we tell the bot to execute this in an asynchronous 1/2
        #fashion meaning it will allow other parts of the program (like play and queue commands) to function correctly without stopping just for this one command. 2/2

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client #Checks for previous voice client association
    song_queue.clear() #Clears the queue on sending of the /stop command

    if voice_client: #if the bot is in the voice client then await disconnection from whatever voice channel it was playing in
        await voice_client.disconnect() 



@bot.command()
async def play(ctx, *, searchresults):
    try:
        voice_channel = ctx.author.voice.channel
    except AttributeError:
        embed = discord.Embed(
            title="Error:",
            description="You need to be in a voice channel to use this command.",
            color=0x6b30d9
        )
        embed.set_author(name="Prismo")
        return await ctx.send(embed=embed)

    permissions = voice_channel.permissions_for(ctx.me)
    if not permissions.connect or not permissions.speak:
        embed = discord.Embed(
            title="Error:",
            description="I don't have permission to join or speak in that voice channel.",
            color=0x6b30d9
        )
        embed.set_author(name="Prismo")
        return await ctx.send(embed=embed)

    voice_client = ctx.guild.voice_client
    if not voice_client:
        await voice_channel.connect()
        voice_client = ctx.guild.voice_client

    ytdl = yt_dlp.YoutubeDL(ydl_opts)

    if "youtube.com" in searchresults or "youtu.be" in searchresults:
        data = ytdl.extract_info(url=searchresults, download=False)
    else:
        data = ytdl.extract_info(f"ytsearch:{searchresults}", download=False)

    if 'entries' in data:
        data = data['entries'][0]

    title = data.get('title', 'Unknown Title')
    song_url = data.get('url', '')

    if bot.is_playing or len(song_queue) > 0:
        # If a song is playing or there are songs in the queue, add to the queue
        song_queue.append((title, song_url))
        embed_msg = "Added to Queue"
    else:
        # If no song is playing and the queue is empty, play the song immediately
        await play_song(ctx, song_url)
        embed_msg = "Now Playing"

    # Create an embed to show the added/playing song's title
    embed = discord.Embed(
        title=embed_msg,
        description=f"**{title}** has been {embed_msg.lower()}.",
        color=0x6b30d9
    )
    embed.set_author(name="Prismo")
    await ctx.send(embed=embed)


async def play_next(ctx):
    if len(song_queue) > 0:
        next_song = song_queue.pop(0)
        await play_song(ctx, next_song[1])  # Use the song URL for playback

        # Send an embed for the "Now Playing" message
        await ctx.send(embed=discord.Embed(
            title="Now Playing",
            description=f"**{next_song[0]}**",
            color=0x6b30d9
        ).set_author(name="Prismo"))
    else:
        bot.is_playing = False

async def play_song(ctx, song_url):
    voice_client = ctx.voice_client
    bot.is_playing = True

    def after(error):
        if error:
            print(error)

        # Check if there are more songs in the queue
        if len(song_queue) > 0:
            next_song = song_queue[0]
            voice_client.play(discord.FFmpegPCMAudio(next_song[1], **ffmpeg_options), after=lambda e: after(e))
            song_queue.pop(0)  # Remove the played song from the queue
        else:
            bot.is_playing = False

    # Play the current song
    voice_client.play(discord.FFmpegPCMAudio(song_url, **ffmpeg_options), after=lambda e: after(e))

        

@bot.command(aliases=['queue'])
async def q(ctx):
    if not song_queue:
        # Handle an empty queue
        embed = discord.Embed(
            title="Queue",
            description="The queue appears to be empty. Use /play to add songs!",
            color=0x6b30d9
        )
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)
    else:
        # Iterate through the queue and display song titles
        queue_list = '\n'.join([f"{index + 1}. {song[0]}" for index, song in enumerate(song_queue)])
        
        embed = discord.Embed(
            title="Queue",
            description="All currently queued songs in order",
            color=0x6b30d9
        )
        embed.set_author(name="Prismo")
        embed.add_field(name="Current Queue:", value=queue_list, inline=False)  
        await ctx.send(embed=embed)        

@bot.command()
async def shuffle(ctx):
    if len(song_queue) < 2:
        embed = discord.Embed(title="Error:", description="There are not enough songs in the queue to shuffle :( ", color=0x6b30d9)
        embed.set_author(name="Prismo")
        return await ctx.send(embed=embed)

    else:
        random.shuffle(song_queue)
        embed = discord.Embed(title="Queue", description="Queue has been shuffled :) ", color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed) 

@bot.command()
async def clearqueue(ctx):
    song_queue.clear()
    embed = discord.Embed(title="The queue has now been cleared", color=0x6b30d9)
    await ctx.send(embed=embed) 

@bot.command()
async def clear(ctx):
    song_queue.clear()
    embed = discord.Embed(title="The queue has now been cleared", color=0x6b30d9)
    await ctx.send(embed=embed)

@bot.command()
async def remove(ctx, index: int):
    if 1 <= index <= len(song_queue):
        trash_song = song_queue.pop(index - 1)
        embed = discord.Embed(title="Removed:", description=f"{trash_song[0]}, from the queue.", color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:", description="Invalid song ID number, please try again.", color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed) 

import asyncio

@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        
        if song_queue:
            await play_next(ctx)  # Call play_next directly after stopping the current song
            
        else:
            embed = discord.Embed(title="No more songs in the queue.", color=0x6b30d9)
            await ctx.send(embed=embed)
            
    else:
        embed = discord.Embed(title="Error", description="No song is currently playing", color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)

@bot.command()
async def pause(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client and voice_client.is_playing():
        voice_client.pause()
        embed = discord.Embed(title="Now Paused :pause_button:", color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:", description= "No music is currently playing." ,color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)

@bot.command()
async def resume(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client and voice_client.is_paused():
        voice_client.resume()
        embed = discord.Embed(title="Now Resumed :arrow_forward:", color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:", description= "No music is currently paused." ,color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)

@bot.command(aliases=['np', 'currentsong', 'playingnow', 'now playing'])
async def nowplaying(ctx):
    if song_queue:
        current_song = song_queue[0]
        embed = discord.Embed(title="Currently playing:", description=current_song[0], color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error:", description="No song is currently playing.", color=0x6b30d9)
        embed.set_author(name="Prismo")
        await ctx.send(embed=embed) 

@bot.event
async def on_message(message):
    await bot.process_commands(message)

TOKEN = 'MTE0MTQ3MDMyMDIyMjU1NjI1MQ.GGUiM0.O_-sn8Csf1QR2eNFmWKGSfiDcSaXpNPNXqEkCc'
bot.run(TOKEN)