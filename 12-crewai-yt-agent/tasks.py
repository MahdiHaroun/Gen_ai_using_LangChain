# 2tasks 
from crewai import Task 
from tools import yt_tool
from agents import blog_researcher , blog_writer




research_task = Task(
    description = (
        'identify the relevant video content for the topic {topic} from yt channel {channel}'
        'Get detailed information about the video from the channel {channel} related to {topic}'
    ),
    expected_output = 'A comprehensive 3 paragraphs long report based on the {topic} from the {channel} channel',
    tools = [yt_tool], 
    agent = blog_researcher , 
    )


write_task = Task(
    description = (
        'Narrate compelling blog post for the topic {topic} using information from the {channel} channel'
    ),
    expected_output = 'A compelling blog post for the topic {topic} using information from the {channel} channel',
    tools = [yt_tool], 
    agent = blog_writer , 
    async_execution = False , # True makes agent works parallelly 
    output_type = 'file',
    output_file = 'blog_post.md'
    )  