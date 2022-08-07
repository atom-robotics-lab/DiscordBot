import  discord
import  time
from matplotlib.style import context 
from    tabulate        import tabulate
from    discord.ext     import tasks
from    BotFunctions    import *




intents                          =      discord.Intents.default()
intents.members                  =      True
intents.reactions                =      True
client                           =      discord.Client(intents=intents)
# ui                               =      UI(client)


start_event_flag                 =  False
manual_attendnce_flag            =  False
automatic_attendance_flag        =  False 
poll_flag                        =  False
game_flag                        =  False


poll_list                        =  {}
id_member                        =  0
update_live_status_msg           =  " "
update_live_status_msg_heading   =  " "
Meeting_time_update              =  " "
Poll_msg                         =  " "
epoch                            =  0   # necessary 



@tasks.loop(seconds= 10.0)    # --------------------->  done 

async def schedule_meeting():
    global epoch 
    Schedule_meeting()  
    await update_live_status_msg.edit(content ='```\n{}\n```'.format(update_live_status_member()))
    await Meeting_time_update.edit(content = '```\nTotal Meeting time : {} mins \n```'.format(round((time.time()-epoch)/60,0)))
   


@client.event                     # --------------------------> done 
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message): 

    global start_event_flag
    global manual_attendnce_flag
    global automatic_attendance_flag

#                           |--------------- If bot call itself it will return nothing  ---------------| 
    if message.author == client.user:    # ---------------> done 
        return

#                           |--------------- When Event is Started (CMD - *start_event) ---------------| 

    if message.content.startswith('*start_event'): # -------> DONE 
        if message.author.id in author_list:
            if start_event_flag == False: 
                await message.channel.send(Start_event(message.content[13:]))
                start_event_flag = True
            else:
                await message.channel.send("Session already started")
        else:
            await message.channel.send(":no_entry_sign:```\nUnauthorized Access\n```")

#                           |--------------- Manual Way of attendance   (CMD - *attend_m) ---------------| 

    if message.content.startswith("*attend_m"):
        if message.author.id in author_list:
            if (start_event_flag == True and manual_attendnce_flag == False):
                await message.channel.send(":wave:```\nHey Users !! To mark you attendance , call this cmd  '*attendance' \n```")
                manual_attendnce_flag = True
            else:
                await message.channel.send("Start a event to call this cmd OR this cmd is been called earlier !!  ")
        else:
             await message.channel.send(":no_entry_sign:```\nUnauthorized Access\n```")

#                           |--------------- To mark attendance by the users   (CMD - *attendance) ---------------| 


    if message.content.startswith("*attendance"):
        if (start_event_flag == True and manual_attendnce_flag == True) :
            await message.channel.send(">>> :100: Attendance registered {}".format(message.author.mention))
        else:
            await message.channel.send("```\nNo current event Registered\n```")


#                           |--------------- Virtual Way of attendance   (CMD - *attend_v) ---------------| 

    if message.content.startswith("*attend_v"):  # done 
        global id_member
        global update_live_status_msg
        global update_live_status_msg_heading
        global Meeting_time_update


        if message.author.id in author_list:
            global epoch 
            id_member = VoiceChannels(message.content[10:])
            if(id_member!=None):  
                if (start_event_flag == True and automatic_attendance_flag == False):

                    Attend_v(client.get_channel(id_member).members)
                    epoch = time.time()

                    update_live_status_msg_heading      =   await message.channel.send('```arm\nLIVE_STATUS \n``` ') 
                    update_live_status_msg              =   await message.channel.send('```\n{}\n```'.format(update_live_status_member()))
                    Meeting_time_update                 =   await message.channel.send('```\nTotal Meeting time : {} mins \n```'.format(round((time.time()-epoch)/60,1)))

                    automatic_attendance_flag = True
                    schedule_meeting.start()
                    
                else:
                    await message.channel.send("```Start a event to call this cmd OR this cmd is been called earlier !! ```")
            else:
                 await message.channel.send("Enter valid voice channel name `cmd format - *attend_v {Channel Name"+"}`")
        else:
             await message.channel.send(":no_entry_sign:```\nUnauthorized Access\n```")


#                           |--------------- To End Event (CMD - *end_event) ---------------| 

    if message.content.startswith("*end_event"):   # done
        if message.author.id in author_list:
            if start_event_flag == True:
                await message.channel.send(">>> :wave: `Session End`")
                start_event_flag = False
                manual_attendnce_flag = False
                automatic_attendance_flag = False
                 
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


#                           |--------------- To Publish Data to Google Sheet (CMD - *publish_data) ---------------| 

    if message.content.startswith("*publish_data"):  # done 
        if message.author.id in author_list: 
            publishData(live_status_member)
        else:
            await message.channel.send("Unauthorized Access")

#                           |--------------- To Retrieve Data from Google Sheet (CMD - *get_attendance) ---------------|

    if message.content.startswith("*get_attendance"): 
        if message.author.id in author_list:
            head = ["Name", "Attendance in %"]
            await message.channel.send(f'```\n{tabulate(Get_attendance(message.content[15:]), headers=head, tablefmt="psql")}\n```')         
        else:
            await message.channel.send("Unauthorized Access")

# | ------------------------------------------------------------------------ |

    if message.content.startswith("*game"): 
        if game_flag == False:
             game_flag == True

        try:
             r = message.content[6:]
             x = r.split("<")
             s,t = x[1],x[2]
             s,t = s.split() , t.split()
             x[1] , x[2] = s , t 
             player_1 , player_2 = x[1][0][1:len(x[1][0])-1] , x[2][0][1:len(x[2][0])-1]
             player_1_chance = 0
             player_2_chance = 0 

             box = await message.channel.send("```\n{}\n```".format(TickTocToe(message,player_1,player_2,1,0,0)))
             box_msg = await message.channel.send("```GAME B/W    {}    &    {}\n```"
                                                       .format("Player-1","Player-2")+
                                                       " "*12+"<@{}>".format(player_1)+
                                                       " "*12+"<@{}>".format(player_2))


             while(True):
                 msg = await client.wait_for('message')
                 if (str(msg.author.id) == player_1 or str(msg.author.id) == player_2):
                    board , board_message , player_1_chance , player_2_chance ,value = TickTocToe(msg,player_1,player_2,2,player_1_chance,player_2_chance)
                    await box.edit(content="```\n{}\n```".format(board))
                    if player_2_chance+player_1_chance == 9:
                        board_message = " Its a DRAW guys !! "
                    await box_msg.edit(content="```\n {}\n```".format(board_message))
                    await msg.delete()
                    print(player_1_chance,player_2_chance)
                    if value == True :
                        break 
    
        except:
          await message.channel.send("Something went wrong try with proper cmmds \n `@<player_1> @<player_2`") 




    if message.content.startswith("*announcement"): # done 
        if message.author.id in author_list: 
            announcement_content   =   message.content[14:].strip()
            
            embed = discord.Embed(title='ㅤㅤㅤㅤㅤㅤㅤㅤ:exclamation:Announcement:exclamation:',description = "```\n{}\n```".format(announcement_content),color = discord.Color.red())
            embed.set_image(url=Announcement_image_url)
            embed.add_field(name = 'Tags', value= "{}".format(message.guild.default_role))
            await message.channel.send(embed=embed)
            
        else:
            await message.channel.send("Unauthorized Access")

#                           |--------------- Poll  ---------------| 

    if message.content.startswith("*poll"): # done 
        global Poll_msg
        global poll_flag
        global num_of_polls
          

        try :
            num_of_polls  = int(message.content[6] + message.content[7])               
            Poll_msg =  await message.channel.send( Poll(num_of_polls, message.content[9:].strip()))
            poll_flag = True
        except:
            await message.channel.send(":rolling_eyes: `Enter number of POLL option as int`")

#                           |--------------- Poll  ---------------|
    if message.content.startswith("*get_poll_result"):   # done 
        try:
            s = ">>>      **Polling Result**\n*Options*    *Vote(s)* "
            await Poll_msg.add_reaction("1️⃣")
            for keys in poll_list:
                s = s + "\n{}                      `{}`      `{}`".format(keys,len(poll_list[keys]),' #'*len(poll_list[keys]))
            s = s + "\n"
            await Poll_msg.reply(s)
        except:
            await message.channel.send("```No Active Poll```")
  
@client.event
async def on_reaction_add(reaction, user):
    global poll_list
    if reaction.message == Poll_msg :
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
    # if reaction.message == Poll_msg and poll_flag == True:
        try:
             poll_list[str(reaction)].remove(user.name)
        except:
            pass

#                           |--------------- This function is called when there is a change of stste in a voice state ---------------|
@client.event
async def on_voice_state_update(member, before, after):
    global live_status_msg
    global id_member
    global update_live_status_msg
   

                                           
    if member.name not in live_status_member:                                                                 
        if(after.channel != None):                                                                             
            if(id_member == after.channel.id ):                                                                
                if(update_live_status_msg != " " ) :                                                                                     
                    live_status_member[member.name] = [0 ,'Active', round(time.time(),0)]                                                                                   
                    await update_live_status_msg.edit(content ='```\n{}\n```'.format(update_live_status_member()))       


    elif member.name in live_status_member:         
            if(after.channel != None ):              
                if(after.channel.id == id_member):                  
                    if(before.channel != None ):                      
                        if(before.channel.id != id_member):                            
                            if(update_live_status_msg != " " ) : 
                                VoiceStateChange(member.name)                                                                              
                                await update_live_status_msg.edit(content ='```\n{}\n```'.format(update_live_status_member()))
                    else: 
                        if(update_live_status_msg != " " ) :
                            VoiceStateChange(member.name)                                                                                           
                            await update_live_status_msg.edit(content ='```\n{}\n```'.format(update_live_status_member()))
            
    
    if (before.channel != None  ):
        if(before.channel.id == id_member):
            if(after.channel != None ):
                if(after.channel.id != id_member):
                    if(update_live_status_msg != " " ) :
                        VoiceStateChange_2(member.name)                        
                        await update_live_status_msg.edit(content ='``` \n{}\n```'.format(update_live_status_member()))  
            else:
                 if(update_live_status_msg != " " ) :                     
                    VoiceStateChange_2(member.name)                        
                    await update_live_status_msg.edit(content ='``` \n{}\n```'.format(update_live_status_member()))  


    
   
   
                                    

client.run("")

