import os 
from discord.ext import commands 
import pymysql 
import json 
import datetime 
import requests
import logging 
#role_names = [role.name for role in author.roles]
#if "BotModerator" in role_names

logging.basicConfig(filename='ServerLog.log', level=logging.DEBUG)
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
    logging.warning("[{}]MySql Server Error".format(datetime.datetime.now()))

def GetUserName(uuid):
    mojang_api = 'https://api.mojang.com/user/profiles/'+uuid+'/names' 
    res = requests.get(mojang_api)
    return res[-1]['name']

@AuthBot.event
async def on_ready():
    print("Logged in as")
    print(AuthBot.user.name)
    print(AuthBot.user.id)
    print("------------------")
    logging.info("[{}]{} and {} ready".format(datetime.datetime.now(), AuthBot.user.name, AuthBot.user.id))

@AuthBot.command()
async def auth(ctx, code):
    logging.info("[{}]{} tried /auth {}".format(datetime.datetime.now(), ctx.message.author, code))
    UserName = ctx.message.author.name
    UserID = ctx.message.author.id 
    if 'Authenticated' in ctx.message.author.roles:
        logging.info("[{}]{} tried /auth {} But, Already authenticated".format(datetime.datetime.now(), UserName))
        ctx.send("Already authenticated! Have a good time~!")
    else:
        #check auth code in database 
        now = datetime.datetime.now()
        SearchUserCodeSql = "select * from {} where auth_code={} {} < expire_date and permission=0".format(auth_table, code, now)
        MysqlCursor.execute(SearchUserCodeSql) ##use try except 
        
        if MysqlCursor.rowcount == 0:
            logging.info("[{}]isn't exist verificate auth code or was expired auth code about {}".format(datetime.datetime.now(), UserName))
            ctx.send("isn't exist verificate auth code or was expired your code! plz auth in game again!")
        else: 
            row = MysqlCursor.fatchone()
            UpdateUserSql = 'update {} set permission = 1 where index = {}'.format(auth_table, row['index'])
            logging.info("[{}]{} Update Authenticated user set permission in auth_table".format(datetime.datetime.now(), UserName))
            MysqlCursor.execute(UpdateUserSql)
            
            MinecraftName = GetUserName(row['uuid'])
            await bot.change_nickname(ctx.message.author, MinecraftName) #change nickname
            
            Addrole = get(ctx.message.server.roles, name='Authenticated')
            Rmrole =get(ctx.message.server.roles, name='Not-Authenicated')
            if Addrole and Rmrole:
                await client.add_role(ctx.message.author, Addrole)
                await client.remove_role(ctx.message.author, Rmrole)
            logging.info("[{}] Set {}'s role'".format(datetime.datetime.now(), UserName))


if __name__ == "__main__":
    ServerEnv = GetServerEnv()
    AuthBot.run(ServerEnv['token'])
    MysqlConnect.close()
