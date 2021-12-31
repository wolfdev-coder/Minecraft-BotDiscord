import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType, Context
from discord.utils import get
from mcrcon import MCRcon
import requests
import random
import asyncio
import sqlite3
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption, ActionRow
import discord_components
import dislash
from dislash import InteractionClient, ContextMenuInteraction
import multitasking

mcr = MCRcon("217.106.107.160", "123", port = 30570)
mcr.connect()

client = commands.AutoShardedBot(command_prefix = 'e.', intents = discord.Intents.all(), case_insensitive = True, owner_id = 561782733345390602, strip_after_prefix = True)
client.remove_command('help')

connection = sqlite3.connect('password.db')
cursor = connection.cursor()

@client.event
async def on_ready():
    print('Бот запущен')
    DiscordComponents(client)
    cursor.execute( """CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        m2a INT,
        pass INT
    )""")
    connection.commit()
    await m2a()

async def m2a():
    while True:
        for row in cursor.execute("SELECT name, id, m2a, pass FROM users").fetchall():
            if int(row[2]) == 1:
                try:
                    list_p = mcr.command('cmi list')
                except:
                    list_p = []
                if str(row[0]) in list_p:
                    if str(row[3]) == '1':
                        pass
                    else:
                        s2 = True
                        code = random.randint(10000, 99999)
                        mcr.command(f'gm 2 {row[0]}')
                        member = client.get_user(int(row[1]))
                        await member.create_dm()
                        coint = 0
                        pos = mcr.command(f'pos {row[0]}')
                        pos = pos[pos.index(',')+1:]
                        pos = pos[:pos.index(')')]
                        pos = pos.replace('§6', '').replace('§e', '')
                        pos = pos.split(':')
                        while s2:
                            mcr.command(f'minecraft:tp {row[0]} {pos[0]} {pos[1]} {pos[2]} 0 180')
                            mcr.command(f'title {row[0]} title "Введите данный код в §9дс: §l§6{code}"')
                            coint += 1
                            if coint == 5:
                                async for message in client.get_channel(member.dm_channel.id).history(limit=1):
                                    if str(code) == str(message.content):
                                        s2 = False
                                        mcr.command(f'gm 0 {row[0]}')
                                        cursor.execute("UPDATE users SET pass = 1 WHERE id = {}".format(row[1]))
                                        connection.commit()
                                coint = 0
                else:
                    cursor.execute("UPDATE users SET pass = 0 WHERE id = {}".format(row[1]))
                    connection.commit()

client.run('ODc4NjcwOTY2ODE1ODYyODQ1.YSEkGw.ZoSt4vTYlirlVcQZumrutKjU86o')
