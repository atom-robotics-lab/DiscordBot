from    datetime    import date 
import  time
from    tabulate    import tabulate
import  requests


session_name = " " 
live_status_member               =  {}
game_board                       =  " "
lt = [
         ["  ","  ","  "],
         ["  ","  ","  "],
         ["  ","  ","  "]
                      ]


author_list = [   

    624095315527467018,      #     process_singh         
    492013542908755978,      #     brad              
    389095932681125890,      #     hazor              
    627173256251703307,      #     insaanimanav     
    808610370767159298,      #     mr_no man            
    460176086286729216,      #     jc                
    549960854628466699,      #     topguns
    689558174168121370       #     divyansh
              ]

VoiceChannel_list = {

    "meeting room 1": 916727426950778931,  # meeting Room 1
    "meeting room 2": 916727713438527548,  # meeting room 2 
    "chill zone"    : 906159392389464164,  # chill zone
    "lounge"        : 906144295197765692,  # lounge
    "seminar hall"  : 908393705906507777,  # seminar hall
    "gaming"        : 906144295197765693,  # meeting room 
    "general"       : 896769550614401059,  # General       --- >   # jc server 
    "voice_channel" : 996820281102434407,  # Voice_cahnnel ------> # jc  server
    "admin"         : 906801469544607754   # admin channel 
                     }


Url_PublishData  = 'https://script.google.com/macros/s/AKfycbyJbP2JKm29JHdkpdxzvCdefhAqUPlXviqLimFwNNR3xFklFYy-SARPcYG1fds1eAfi/exec'
Url_RetrieveData = 'https://script.google.com/macros/s/AKfycbyobDOcV-xZYecZ7PJfCBV23w6emsRyxNtYK6Vs1il_yc_sfnxWC7e4fhpDVZb0A0n8/exec'
Announcement_image_url = 'https://raw.githubusercontent.com/jchaudhary21/test/main/ezgif.com-gif-maker.gif'


# ----------------------------------------- FUNCTIONS ----------------------------------------- # 

# Function which converts channel name into its Discord id  
def VoiceChannels(voicechannel_name):
    try :
        id = VoiceChannel_list[str(voicechannel_name).lower()]   
        return id                        # Return id if channel name if there in VoiceChannel List
    except :
        return None                      # if Not then it will return None. 



# Function which print necessary info when any session/ event is started  
def Start_event(msg_content):     
    global session_name                  # making session_name global so that it can be used by other functions with updated values                       
    session_name = msg_content           # Updating session_name with latest values 
    return (">>> "+" "*8 +               # returning msg 
    "        **Session Registered**" 
    +"```\nDate : -  {}\nSession Name :-  {}\n```"
    .format(date.today().strftime("%d %B %Y")
    ,session_name))  


# Function is called when attend_v call is called basically it initialize  all the value 
def Attend_v(members_voicechannel):

    for member in members_voicechannel:   # assigning initial values to all the members who are there in the mention channel  
            live_status_member[member.name]  = [0 ,'Active', round(time.time(),0)]

    
# Function is called when tabular form of members is needed basically it convert dictionary into table  
def update_live_status_member():
    temp_list = {}  
    for x in live_status_member:
        first , second      = live_status_member[x][0],live_status_member[x][1] # converting dictionary into list as tabulate library only take list as input 
        temp_list[x] = [first ,second]
    list1                   = list(temp_list.items())                           
    head                    = ["Name", "[Time log (mins) , Status ]"]           
    return tabulate(list1, headers=head, tablefmt="psql")


# Function is repeatedly called to update member list 
def Schedule_meeting():
    for x in live_status_member :
        previous_time = live_status_member[x][0]
        status = live_status_member[x][1]
        join_time = live_status_member[x][2]
        if ( status != 'In-active'):
            live_status_member[x] = [round(previous_time + (round(time.time(),1) - join_time)/60,1),status,round(time.time(),1)] 
            

# Function is called to publish data to google sheet 
def publishData(dict_live):
    dict_keys     = []                                  # this python script and google sheet communicate through json 
    pub_dict      = {"date":(date.today().strftime("%d %B %Y")) +f' / {session_name}', "number":len(live_status_member)}  
    for key in dict_live:
        dict_keys.append(key)
    for x in range(0,len(dict_live)):                   # converting data into json  
       pub_dict["name_{}".format(x+1)] = dict_keys[x]   
    requests.post(Url_PublishData,json=pub_dict)        # finally publish data 
    pub_dict.clear()  
    live_status_member.clear()                                   


# Function is called to get attendance , basically it fetch data from google sheet and show it into tabular form 
def Get_attendance(msg_content):
    x = requests.get(Url_RetrieveData) 
    if(msg_content == ''):
        member_name =  x.json()
        for key in x.json():
            member_name[key] = f'{round(float((member_name[key])),2)*100} %'
        member_name_list = list(member_name.items())
        return member_name_list       
    else:
        member_name =  x.json()
        try:
            member_name = {msg_content:f'{round(float(msg_content),2)*100} %'}
            member_name_list = list(member_name.items())
            return member_name_list
        except:
             return '```\nNo such name is there\n```'


# Function to generate poll 
def Poll(num_of_polls,msg_content):
        emoji_list = [' :one:',' :two:',' :three:',' :four:',' :five:',' :six:',' :seven:',' :eight:',' :nine:'] 
        if (num_of_polls < 10 and  num_of_polls >0 ):
            msg_content   =   msg_content
            s=" " 
            for i in range(0,num_of_polls):
                    s = emoji_list[i] + s
            return ('>>> ㅤㅤㅤㅤㅤㅤㅤㅤ:exclamation:**POLL TIME**:exclamation: ```\n{}\n``` \n  `React with following emojis`\n{}'.format(msg_content,s))
        else:
            return (":rolling_eyes: `Can't create poll option more than 10 or less than zero`")

def VoiceStateChange(member_name):
    previous_time = live_status_member[member_name][0]
    live_status_member[member_name] = [round(previous_time,2),'Active',round(time.time(),0)] 

def VoiceStateChange_2(member_name):
    last_join = live_status_member[member_name][2]
    previous_time = live_status_member[member_name][0]
    live_status_member.update({member_name : [ round((time.time() - last_join)/60 ,2) + previous_time,'In-active', last_join]})

def TickTocToe(message,player_1,player_2,no,player_1_chance,player_2_chance):
    try:  
        if no == 1:
            return (PrintBoard())
        if no == 2:
        # print(message.content , message.author.id , player_1 , player_2)
            if str(message.author.id) == player_1 or str(message.author.id) == player_2:
                if(player_1_chance==player_2_chance):
                    if str(message.author.id) == player_2:
                        return (PrintBoard(),"Player_1 chance ",player_1_chance,player_2_chance,False)
                    elif(str(message.author.id) == player_1):
                        y,x = int(message.content[1]),int(message.content[3])
                        if(lt[y-1][x-1]=="  "):
                            lt[y-1][x-1] = "X"
                            value = check()
                       
                        #  "\nGame between <@{}> v/s <@{} \n <@{}> first then <@{}>".format(player_1,player_2,player_1,player_2)
                            return (PrintBoard(),("GAME B/W    {}    &    {}"
                                                       .format("Player-1","Player-2")+
                                                       " "*12+"<@{}>".format(player_1)+
                                                       " "*12+"<@{}>".format(player_2)),player_1_chance+1,player_2_chance,value)
                        else:
                            return (PrintBoard(),"{} is already there ".format(lt[y-1][x-1]),player_1_chance,player_2_chance,False)
                    
                elif(player_1_chance>player_2_chance):
                    if str(message.author.id) == player_1:
                        return (PrintBoard(),"Player_2 chance",player_1_chance,player_2_chance,False)
                    elif(str(message.author.id) == player_2):
                        y,x = int(message.content[1]),int(message.content[3])
                        if(lt[y-1][x-1]=="  "):
                            lt[y-1][x-1] = "O"
                            value = check()
                            return  (PrintBoard(),("```GAME B/W    {}    &    {}\n```"
                                                       .format("Player-1","Player-2")+
                                                       " "*12+"<@{}>".format(player_1)+
                                                       " "*12+"<@{}>".format(player_2)),player_1_chance,player_2_chance+1,value)
                        else:
                            return (PrintBoard(),"{} is already there ".format(lt[y-1][x-1]),player_1_chance,player_2_chance,False)

    except:
            return (PrintBoard(),"some cmmd error is there".format(lt[y-1][x-1]),player_1_chance,player_2_chance,False)


def PrintBoard():
    s =                ( "╒════════════════╕\n"+
                        "   𝚃𝚒𝚌-𝚃𝚊𝚌-𝚃𝚘𝚎  \n"+
                        "╘════════════════╛")


    t = tabulate( lt, tablefmt="fancy_grid" )
    a =','.join(t.splitlines())
    x = a.split(",")
    letters = ['₁','₂','₃']
    for i in range(0,len(x)):
            if((i+1)%2 != 0):
                 x[i] = " " + x[i]
            else:
                 x[i] = letters[int((i)/2)]+x[i] 
    p = "  "
    for i in range (0,len(x)):
        p = p + x[i] + "\n" + "  "
    return str(s+"\n     ₁   ₂   ₃"+"\n"+p)


def check():
    print("this is called 2")
    # for diagonal check 
    if(lt[0][0]==lt[1][1]==lt[2][2] != "  " ):
        lt[0][0]= lt[1][1]= lt[2][2] = "!"
        return True
    elif(lt[0][2]==lt[1][1]==lt[2][0] != "  "):
        lt[0][2]=lt[1][1]=lt[2][0] = "!"
        return True
    # for horizontal check
    elif(lt[0][0]==lt[0][1]==lt[0][2]!= "  "):
        lt[0][0]=lt[0][1]=lt[0][2] = "!"
        return True
    elif(lt[1][0]==lt[1][1]==lt[1][2]!= "  "):
        lt[1][0]=lt[1][1]=lt[1][2] = "!"
        return True
    elif(lt[2][2]==lt[2][1]==lt[2][2]!= "  "):
        lt[2][2]=lt[2][1]=lt[2][2] = "!"
        return True
      # for vertical check 
    elif(lt[0][0]==lt[1][0]==lt[2][0]!= "  "):
        lt[0][0]=lt[1][0]=lt[2][0] = "!"
        return True
    elif(lt[0][1]==lt[1][1]==lt[2][1]!= "  "):
        lt[0][1]=lt[1][1]=lt[2][1] = "!"
        return True
    elif(lt[0][2]==lt[1][2]==lt[2][2]!= "  "):
        lt[0][2]=lt[1][2]=lt[2][2] ="!"
        return True
    else :
        return False

if __name__ == "__main__":
    pass