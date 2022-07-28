from unicodedata import name
import  discord
import  requests
from    datetime    import date ,datetime
import  time
from    pytz        import timezone 
from    tabulate    import tabulate
from    discord.ext import tasks

#----------------------------------------------------------#
# Enter discord IDs of those who have the admin rights . 
author_list = [   ]     


#-------------------------------------------------------------#
# Enter name of Voice channels along with there discord IDs.
# Example --  {"General": 0923434578545485}
VoiceChannel_list = { } 

#-------------------------------------------------------------#
Url_PublishData  = '' # Url of app script to send data  
Url_RetrieveData = '' # Url of app script to receive data 


#-------------------------------------------------------------#
# Granting permissions and initializing some values 
intents                          =  discord.Intents.default()
intents.members                  =  True
intents.reactions                 =  True
client                           =  discord.Client(intents=intents)


Today                            =  date.today().strftime("%d %B %Y")
start_event_flag                 =  False
manual_attendnce_flag            =  False
automatic_attendance_flag        =  False 
poll_flag                        =  False


live_status_member               =  {}
poll_list                        =  {}
id_member                        =  0
epoch                            =  0 
update_live_status_msg           =  " "
live_status_msg                  =  " "
now                              =  " "
update_live_status_msg_heading   =  " "
Meeting_time_update              =  " "
session_name                     =  " "
Poll_msg                         =  " "

#-------------------------------------------------------------#
#                                   FUNCTIONS 

# This function is used to  retrieve VoiceChannel ID  from Voice_channel list
# As you pass the channel name 
def VoiceChannels(voicechannel_name):
    try :
        id = VoiceChannel_list[str(voicechannel_name).lower()]
        return id
    except :
        return None        


# This is used to get currently active member list in VoiceChannel  
def members_list(id):
    global now 
    global epoch 
    channel                 = client.get_channel(id) 
    members_voicechannel    = channel.members 

    for member in members_voicechannel:
        live_status_member[member.name]  = [0 ,'Active', round(time.time(),0)]
    return live_status_member


# Return data of members in Tabular Form 
def update_live_status_member():
    temp_list = {}  
    for x in live_status_member:
        first , second      = live_status_member[x][0],live_status_member[x][1]
        temp_list[x] = [first ,second]
    list1                   = list(temp_list.items())
    head                    = ["Name", "[Time log (mins) , Status ]"]
    return tabulate(list1, headers=head, tablefmt="psql")


# Function to publish data on Google Sheet 

def publishData(dict_live):
    dict_keys     = []
    pub_dict      = {"date":Today+f' / {session_name}', "number":len(live_status_member)}  
    for key in dict_live:
        dict_keys.append(key)
    for x in range(0,len(dict_live)):
       pub_dict["name_{}".format(x+1)] = dict_keys[x]
    requests.post(Url_PublishData,json=pub_dict) 
    pub_dict.clear()


#  Function to Update status of member after every particualr Time 
@tasks.loop(seconds= 10.0)
async def schedule_meeting():
    for x in live_status_member :
        previous_time = live_status_member[x][0]
        status = live_status_member[x][1]
        join_time = live_status_member[x][2]
        if ( status != 'In-active'):
            live_status_member[x] = [round(previous_time + (time.time() - join_time)/60 ,2),status,round(time.time(),0)] 
    live_status_msg = update_live_status_member()
    await update_live_status_msg.edit(content ='```\n{}\n```'.format(live_status_msg))
    await Meeting_time_update.edit(content = '```\nTotal Meet time : {} mins\n```'.format(round((time.time()-epoch)/60,2)))

#-------------------------------------------------------------#
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message): 

    global start_event_flag
    global manual_attendnce_flag
    global automatic_attendance_flag

    if message.author == client.user:
        return


# To start a event cmd - *start_event  
    if message.content.startswith("*start_event"): 
        if message.author.id in author_list:
            global session_name
            if start_event_flag == False:
                session_name = message.content[13:]
                await message.channel.send(">>> "+" "*8 +"        **Session Registered**" +"```\nDate : -  %s"%Today + "\nSession Name :-  %s\n```"%(message.content[13:]))
                start_event_flag = True
            else:
                await message.channel.send("Session already started")
        else:
            await message.channel.send(":no_entry_sign:```\nUnauthorized Access\n```")


#  Manual Way of attendance cmd - *attend_m
    if message.content.startswith("*attend_m"):
        if message.author.id in author_list:
            if (start_event_flag == True and manual_attendnce_flag == False):
                await message.channel.send(":wave:```\nHey Users !! To mark you attendance , call this cmd  '*attendance' \n```")
                manual_attendnce_flag = True
            else:
                await message.channel.send("Start a event to call this cmd OR this cmd is been called earlier !!  ")
        else:
             await message.channel.send(":no_entry_sign:```\nUnauthorized Access\n```")


# To mark attendance by the users cmd - *attendance 
    if message.content.startswith("*attendance"):
        if (start_event_flag == True and manual_attendnce_flag == True) :
            await message.channel.send(">>> :100: Attendance registered {}".format(message.author.mention))
        else:
            await message.channel.send("```\nNo current event Registered\n```")


# Virtual Way of attendance cmd - *attend_v 
    if message.content.startswith("*attend_v"):  
        global id_member
        global live_status_msg
        global update_live_status_msg
        global update_live_status_msg_heading
        global Meeting_time_update
        global now
        global epoch 
        if message.author.id in author_list:
            id_member = VoiceChannels(message.content[10:])
            if(id_member!=None):  
                if (start_event_flag == True and automatic_attendance_flag == False):
                    now = datetime.now(timezone("Asia/Kolkata")).strftime('%I:%M:%S')
                    epoch = time.time()
                    members_voicechannel = members_list(id_member)
                    live_status_msg = update_live_status_member()
                    update_live_status_msg_heading = await message.channel.send('```arm\nLIVE_STATUS \n``` ') 
                    update_live_status_msg = await message.channel.send('```\n{}\n```'.format(live_status_msg))
                    Meeting_time_update = await message.channel.send('```\nTotal Meeting time : {} mins \n```'.format(round((time.time()-epoch)/60,1)))
                    schedule_meeting.start()
                    automatic_attendance_flag = True
                else:
                    await message.channel.send("```Start a event to call this cmd OR this cmd is been called earlier !! ```")
            else:
                 await message.channel.send("Enter valid voice channel name `cmd format - *attend_v {Channel Name"+"}`")
        else:
             await message.channel.send(":no_entry_sign:```\nUnauthorized Access\n```")


# To End Event  cmd - *end_event 
    if message.content.startswith("*end_event"):
        if message.author.id in author_list:
            if start_event_flag == True:
                await message.channel.send("------ Session End ------")
                start_event_flag = False
                manual_attendnce_flag == False
                automatic_attendance_flag = False
                live_status_member.clear()  
                schedule_meeting.stop()
                await update_live_status_msg_heading.edit(content="```arm\n ̶L̶I̶V̶E̶ ̶S̶T̶A̶T̶U̶S̶  \n```")  
                update_live_status_msg = " "
                Meeting_time_update = " "
            else:
                start_event_flag = False
                manual_attendnce_flag == False
                automatic_attendance_flag = False
               # live_status_member.clear()
                await message.channel.send("No current event Registered")
                update_live_status_msg = " "
        else:
            await message.channel.send("Unauthorized Acess")


# To Publish Data to Google Sheet cmd - *publish_data 
    if message.content.startswith("*publish_data"): 
        if message.author.id in author_list: 
            publishData(live_status_member)
        else:
            await message.channel.send("Unauthorized Access")


# To Retrieve Data from Google Sheet cmd - *get_attendance
    if message.content.startswith("*get_attendance"): 
        if message.author.id in author_list:
            x = requests.get(Url_RetrieveData) 
            if(message.content[15:] == ''):
               member_name =  x.json()
               for key in x.json():
                member_name[key] = f'{round(float((member_name[key])),2)*100} %'
               member_name_list = list(member_name.items())
               head = ["Name", "Attendance in %"]
               await message.channel.send(f'```\n{tabulate(member_name_list, headers=head, tablefmt="psql")}\n```')
            else:
               member_name =  x.json()
               try:
                member_name = {message.content[16:]:f'{round(float(member_name[message.content[16:]]),2)*100} %'}
                member_name_list = list(member_name.items())
                head = ["Name", "Attendance in %"]
                await message.channel.send(f'```\n{tabulate(member_name_list, headers=head, tablefmt="psql")}\n```')
               except:
                await message.channel.send("```\nNo such name is there\n```")           
        else:
            await message.channel.send("Unauthorized Access")

# To start a Poll  
    if message.content.startswith("*poll"): 
        global Poll_msg
        global poll_flag
        global num_of_polls
        num_of_polls  = message.content[6] 
        emoji_list = [' :one:',' :two:',' :three:',' :four:',' :five:',' :six:',' :seven:',' :eight:',' :nine:'] 
        try :
      
            num_of_polls  = int(message.content[6] + message.content[7]) 
            if (num_of_polls < 10 and  num_of_polls >0 ):
                msg_content   =   message.content[9:].strip()
                s=" " 
                for i in range(0,num_of_polls):
                    s = emoji_list[i] + s
                Poll_msg =  await message.channel.send('>>>       **POLL TIME** ```\n{}\n``` \n {} `React with following emojis`\n{}'.format(msg_content,message.guild.default_role,s))     
                poll_flag = True
            else:
                await message.channel.send(":rolling_eyes: `Can't create polling option more than 10 and more than zero`")
        except:
            await message.channel.send(":rolling_eyes: `Enter number of POLL option as int`")

# To get Poll result
    if message.content.startswith("*get_poll_result"): 
        s = ">>>      **Polling Result**\n*Options*    *Vote(s)* "
        await Poll_msg.add_reaction("1️⃣")
        for keys in poll_list:
            s = s + "\n{}                      `{}`      `{}`".format(keys,len(poll_list[keys]),' #'*len(poll_list[keys]))
        s = s + "\n"
        await message.channel.send(s)
            

@client.event
async def on_reaction_add(reaction, user):
    global poll_list
    if reaction.message == Poll_msg and poll_flag == True:
        emoji_list = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]

        if(str(reaction) not in emoji_list[0:num_of_polls]):
            await Poll_msg.clear_reaction(reaction)

        if(str(reaction) in emoji_list[0:num_of_polls]):
            try:  
                poll_list[str(reaction)].append(user.name) 

            except:
                poll_list[str(reaction)] = [user.name]


@client.event
async def on_reaction_remove(reaction, user):
     if reaction.message == Poll_msg and poll_flag == True:
        try:
             poll_list[str(reaction)].remove(user.name)
        except:
            pass

#  This function is called when there is a change of stste in a voice state 
@client.event
async def on_voice_state_update(member, before, after):
    global live_status_msg
    global now
    global id_member
    global update_live_status_msg
    global epoch 

                                           
    if member.name not in live_status_member:                                                                 
        if(after.channel != None):                                                                             
            if(id_member == after.channel.id ):                                                                
                if(update_live_status_msg != " " ) :                                                                                     
                    live_status_member[member.name] = [0 ,'Active', round(time.time(),0)]                       
                    live_status_msg = update_live_status_member()                                           
                    await update_live_status_msg.edit(content ='```\n{}\n```'.format(live_status_msg))       


    elif member.name in live_status_member:
           
            if(after.channel != None ):              
                if(after.channel.id == id_member):                  
                    if(before.channel != None ):                      
                        if(before.channel.id != id_member):                            
                            if(update_live_status_msg != " " ) :                              
                                previous_time = live_status_member[member.name][0]
                                live_status_member[member.name] = [round(previous_time,2),'Active',round(time.time(),0)]  
                                live_status_msg = update_live_status_member()
                                await update_live_status_msg.edit(content ='```\n{}\n```'.format(live_status_msg))
                    else: 
                         if(update_live_status_msg != " " ) :
                         
                            previous_time = live_status_member[member.name][0]
                            live_status_member[member.name] = [round(previous_time,2),'Active',round(time.time(),0)]  
                            live_status_msg = update_live_status_member()
                            await update_live_status_msg.edit(content ='```\n{}\n```'.format(live_status_msg))
            
    
    if (before.channel != None  ):
        if(before.channel.id == id_member):
            if(after.channel != None ):
                if(after.channel.id != id_member):
                    if(update_live_status_msg != " " ) :
                        
                        last_join = live_status_member[member.name][2]
                        previous_time = live_status_member[member.name][0]
                        live_status_member.update({member.name : [ round((time.time() - last_join)/60 ,2) + previous_time,'In-active', last_join]})
                        live_status_msg = update_live_status_member()
                        await update_live_status_msg.edit(content ='``` \n{}\n```'.format(live_status_msg))  
            else:
                 if(update_live_status_msg != " " ) :
                      
                        last_join = live_status_member[member.name][2]
                        previous_time = live_status_member[member.name][0]
                        live_status_member.update({member.name : [ round((time.time() - last_join )/60,2) + previous_time,'In-active', last_join]})
                        live_status_msg = update_live_status_member()
                        await update_live_status_msg.edit(content ='```\n{}\n```'.format(live_status_msg))  


#-------------------------------------------------------------#    
   
   
                                    

client.run() # <<--- Enter your bot token here 


