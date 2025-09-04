from crewai import Agent
from tools import yt_tool    



## create a senior blog contnet reasearcher 

blog_researcher = Agent(
    role = 'Blog Researcher from Youtube Videos' , 
    goal = 'get the relevent video content for the topic {topic} from yt channel {channel}', 
    verbose = True ,
    memory = True ,
    backstory = ('You are a senior blog content researcher with expertise in extracting relevant information from YouTube videos. Your task is to find and summarize key insights from videos related to {topic} on the {channel} channel.'
    ), 
    tools = [yt_tool], 
    allow_delegation = True # allow for the results forwarding to other agents 


)


## create a senior blog writer agent with YT tools
blog_writer = Agent(
    role = 'Blog Writer from Youtube Videos' , 
    goal = 'Narrate compelling blog post for the topic {topic} using information from the {channel} channel', 
    verbose = True ,
    memory = True ,
    backstory = ('You are a senior blog writer with expertise in crafting engaging blog posts based on insights from YouTube videos. Your task is to create a compelling blog post '
    ), 
    tools = [yt_tool], 
    allow_delegation = False


)