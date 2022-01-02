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
#    client.loop.create_task(m2a())

@client.event
async def on_message(message):
    await client.process_commands(message)

@client.command()
@commands.has_permissions(administrator=True)
async def command(ctx, *, command = None):
    if command is None:
        await ctx.send(embed = discord.Embed(description = f'**{ctx.author.mention}, укажите команду**'))
    else:
        mcr = MCRcon("217.106.107.160", "123", port = 30570)
        mcr.connect()
        p = mcr.command(f'{command}')
        await ctx.send(embed = discord.Embed(description = f'**{p}**'))

def get_log():
    requ = requests.Session()
    req = requ.post('https://ftp.bungee.host/login', data = {
        'host': 'ru1.mineserv.su',
        'username': 'srv41625',
        'password': '00sw0z3a',
        'port': 21,
        'usePassive': 1
        })
    req = requ.get('https://ftp.bungee.host/api?action=getFileContent&file=%2Flogs%2Flatest.log')
    return str(req.text)


@client.command(aliases = ['привязать'])
async def привязка(ctx, player = None):
    if player is None:
        await ctx.send(embed = discord.Embed(description = f'**{ctx.author.mention}, укажите ник игрока на сервере**'))
    else:
        if cursor.execute(f"SELECT name FROM users WHERE id = {ctx.author.id}").fetchone() is None:
            code = random.randint(10000, 99999)
            mcr.command(f'sudo {player} msg {player} §l§9Привязка к Discord: §r§lЧтобы привязать данный аккаунт к аккаунту дискорд ({ctx.author.name}), введите этот код §r§6§l{code}')
            await ctx.send('Вам отправлен **код**, введите его в чат!')
            a = True
            coint = 0
            while a:
                log = get_log()
                log = log.split('\\n')
                log = [log[-1], log[-2], log[-3], log[-4], log[-5], log[-6], log[-7], log[-8], log[-9], log[-10]]
                for x in log:
                    if f'{player}' in x and f'{code}' in x and not 'Rcon' in x and not 'Discord' in x:
                        a = False
                        cursor.execute(f"INSERT INTO users VALUES ('{player}', {ctx.author.id}, 0, 0)")
                        connection.commit()
                        await ctx.send(embed = discord.Embed(description = f'**Вы успешно привязали свой аккаунт!**'))
                await asyncio.sleep(2)
                coint += 1
                if coint == 30:
                    await ctx.send('**Время ожидания вышло!**')
                    a = False
        else:
            await ctx.send(embed = discord.Embed(description = f'**Вы уже привязали аккаунт**'))

@client.command(aliases = ['отвязать'])
async def отвязка(ctx):
    if cursor.execute(f"SELECT name FROM users WHERE id = {ctx.author.id}").fetchone() is None:
        await ctx.send(embed = discord.Embed(description = f'**У вас нет привязанного аккаунта**'))
    else:
        cursor.execute("DELETE FROM users WHERE id = {}".format(ctx.author.id))
        connection.commit()
        await ctx.send(embed = discord.Embed(description = f'**Вы отвязали аккаунт**'))

@client.command(aliases = ['панель', 'инфо', 'ac', 'ак'])
async def аккаунт(ctx):
    if cursor.execute(f"SELECT name FROM users WHERE id = {ctx.author.id}").fetchone() is None:
        await ctx.send(embed = discord.Embed(description = f'**У вас нет привязанного аккаунта**'))
    else:
        Button_list = []
        if int(cursor.execute("SELECT m2a FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]) == 0:
            Button_list.append(Button(style = ButtonStyle.red, label = 'Двухэтапная авторизация', id = f'{ctx.author.id}_m2a'))
        else:
            Button_list.append(Button(style = ButtonStyle.green, label = 'Двухэтапная авторизация', id = f'{ctx.author.id}_m2a'))
        Button_list.append(Button(style = ButtonStyle.red, label = 'Забыл пароль', id = f'{ctx.author.id}_pass'))
        mess = await ctx.send(embed = discord.Embed(title = 'Управление ботом', description = '\n**Выбери действие**'), components = Button_list)

        test_message_coint = 1
        while test_message_coint == 1:
            res = await client.wait_for('button_click')
            if res.component.id == f'{res.author.id}_pass':
                try:
                    code = random.randint(1000000, 9999999)
                    mcr.command(f'nlogin unregister {cursor.execute("SELECT name FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}')
                    mcr.command(f'nlogin register {cursor.execute("SELECT name FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} {code}')
                    await res.respond(embed = discord.Embed(description = f'**Пароль от аккаунта сменён на {code}**'))
                except:
                    await res.respond('Сервер **выключен**!')
            elif res.component.id == f'{res.author.id}_m2a':
                if int(cursor.execute("SELECT m2a FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]) == 0:
                    cursor.execute("UPDATE users SET m2a = 1 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await res.respond(embed = discord.Embed(description = f'**Двухэтапная авторизация включена**'))
                    Button_list[0] = Button(style = ButtonStyle.green, label = 'Двухэтапная авторизация', id = f'{ctx.author.id}_m2a')
                    await mess.edit(components = Button_list)
                else:
                    cursor.execute("UPDATE users SET m2a = 0 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await res.respond(embed = discord.Embed(description = f'**Двухэтапная авторизация выключена**'))
                    Button_list[0] = Button(style = ButtonStyle.red, label = 'Двухэтапная авторизация', id = f'{ctx.author.id}_m2a')
                    await mess.edit(components = Button_list)
                    mcr.command(f'gm 0 {cursor.execute("SELECT name FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}')

async def m2a():
    while True:
        for row in cursor.execute("SELECT name, id, m2a, pass FROM users").fetchall():
            if int(row[2]) == 1:
                try:
                    list_p = mcr.command('list')
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
