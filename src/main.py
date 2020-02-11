import os 
from discord.ext import commands 
import pymysql 
import json 
import datetime 

#role_names = [role.name for role in author.roles]
#if "BotModerator" in role_names

AuthBot = commands.Bot(command_prefix='!')

def GetServerEnv():
    with open('env.json') as EnvFile: 
        ServerEnv = json.load(EnvFile)
    return ServerEnv 

ServerEnv = GetServerEnv()
MysqlConnect = pymysql.connect(host=ServerEnv['host'], user=ServerEnv['username'], password=ServerEnv['password'], db=ServerEnv['dbname'], charset='utf8')
MysqlCursor = MysqlConnect.cursor() 

@AuthBot.event
async def on_ready():
    print("Logged in as")
    print(AuthBot.user.name)
    print(AuthBot.user.id)
    print("------------------")

@AuthBot.command()
async def auth(ctx, code):
    UserName = ctx.message.author.name
    UserID = ctx.message.author.id 
    print(UserName, UserID)
    if 'authenticated' in ctx.message.author.roles:
        ctx.send("Already authenticated! Have a good time~!")
    else:
        now = datetime.datetime.now()
        print(now)
        sql = "select * from {} where auth_code={} and {} < expire_date and permission = {}".format(ServerEnv['auth_table'], code, now, str(0))
        MysqlCursor.execute(sql)
        if MysqlCursor.rowcount == 0:
            ctx.send("isn't exist verificate auth code!")
        else: 
            row = MysqlCursor.fatchone()
            ##TODO update permission and email 
            ##TODO get username from uuid using mojang api https://api.mojang.com/user/profiles/<uuid>/names
            ##TODO change authenticated uers's role and nickname and open vairous channel
            ##TODO logging Server log and check error case 


if __name__ == "__main__":
    ServerEnv = GetServerEnv()
    AuthBot.run(ServerEnv['token'])
    MysqlConnect.close()
