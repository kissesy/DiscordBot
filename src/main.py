import discord
import os
from discord.ext import commands
from discord.utils import get
import pymysql
import json
import datetime
import requests
import logging

logging.basicConfig(filename='ServerLog.log', level=logging.INFO)
AuthBot = commands.Bot(command_prefix='!')

def GetServerEnv():
    try:
        with open('env.json') as EnvFile:
            ServerEnv = json.load(EnvFile)
        return ServerEnv
    except IOError as err:
        logging.warning("[{}]File open error".format(datetime.dateime.now()))

#get Server config file -> json
ServerEnv = GetServerEnv()

try:
    MysqlConnect = pymysql.connect(ServerEnv['host'], ServerEnv['username'], ServerEnv['password'], ServerEnv['dbname'], charset='utf8')
    MysqlCursor = MysqlConnect.cursor(pymysql.cursors.DictCursor)
except pymysql.InternalError as err:
    logging.warning("[{}]MySql Server Error".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

@AuthBot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@AuthBot.event
async def on_ready():
    print("Logged in as")
    print(AuthBot.user.name)
    print(AuthBot.user.id)
    print("------------------")
    logging.info("[{}]{} and {} ready".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), AuthBot.user.name, AuthBot.user.id))


@AuthBot.event
async def on_member_join(member):
    general_id = ServerEnv['general_id']
    general_channel = discord.Guild.get_channel(general_id)
    await general_channel.send_message("Welcome! {} in Lien Server Plz Enter /auth code.".format(member.name))
    Addrole = get(member.guild.roles, id=ServerEnv['Not-Auth_Role'])
    if Addrole:
        logging.info("[{}]Join {} and Set Role({})".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), member.name, Addrole))
        await discord.Member.add_roles(member, Addrole)
    else:
        logging.info("[{}]Couldn't found role! in server in on_member_join function".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def GetUserName(uuid):
    mojang_api = 'https://api.mojang.com/user/profiles/'+uuid+'/names'
    res = requests.get(mojang_api)
    if res.status_code == 200:
        print("[DEBUG] MineCraft Name : ",res.json()[-1]['name'])
        return res.json()[-1]['name']

def JudgeAuth(ctx, RoleName):
    role_names = [role.name for role in ctx.message.author.roles]
    if RoleName in role_names:
        return True
    else:
        return False

def ThrowQuery(sql):
    try:
        MysqlCursor.execute(sql)
    except pymysql.InternalError as err:
        print("ThrowQuery Error")

async def SetRole(ctx):
    Addrole = get(ctx.message.author.guild.roles, id=ServerEnv['Auth_Role'])
    print(Addrole)
    Rmrole = get(ctx.message.author.guild.roles, id=ServerEnv['Not-Auth_Role'])
    print(Rmrole)
    if Addrole and Rmrole:
        await discord.Member.add_roles(ctx.message.author, Addrole)
        await discord.Member.remove_roles(ctx.message.author, Rmrole)
        logging.info("[{}]Success change {}'s role,(remove {} and add {})'".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ctx.message.author.display_name, Rmrole, Addrole))
        return True
    else:
        return False

async def SetName(ctx, MinecraftName):
    await ctx.author.edit(username=MinecraftName) #change nickname
    logging.info("[{}]Change User name from {} to {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ctx.message.author.display_name, MinecraftName))
    print("Set Name")

@AuthBot.command()
async def auth(ctx, code):
    logging.info("[{}]{} tried /auth {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ctx.message.author, code))
    UserName = ctx.message.author.name
    UserID = ctx.message.author.id
    if not(JudgeAuth(ctx, 'Authenticated')):
        print("test")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        SearchUserCodeSql = "select * from {} where auth_code={} and {} < expire_date and permission=0".format(ServerEnv['auth_table'], code, now)
        print(SearchUserCodeSql)
        #SearchUserCodeSql = "select * from {} where auth_code={}".format(ServerEnv['auth_table'], code)
        ThrowQuery(SearchUserCodeSql)
        if MysqlCursor.rowcount == 0:
            await ctx.send("Hey {}! isn't exist verificate auth code or was expired your code! plz auth in game again!".format(UserName))
            logging.info("[{}]{} tried auth but verificated auth code or was expired code!".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), UserName))
        else:
            row = MysqlCursor.fetchone()
            UpdateUserSql = 'update {} set permission = 1 where turn = {}'.format(ServerEnv['auth_table'], row['turn'])
            print(UpdateUserSql)
            ThrowQuery(UpdateUserSql)
            MinecraftName = GetUserName(row['uuid'])
            await SetName(ctx, MinecraftName)
            if not(await SetRole(ctx)):
                print("Set Role Error")
            else:
                print("SEt Role!")
    else:
        await ctx.send("Hey {}! Already Authenticated! Have a good time~!".format(UserName))
        logging.info("[{}]{}! Already Authenticated!".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), UserName)

if __name__ == "__main__":
    ServerEnv = GetServerEnv()
    AuthBot.run(ServerEnv['token'])
    MysqlConnect.close()
