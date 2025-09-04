from crewai import Crew , Process
from agents import blog_researcher , blog_writer     
from tasks import research_task , write_task 

print("Initializing CrewAI...")

crew = Crew( 
    agents = [blog_researcher , blog_writer] ,   
    tasks = [research_task , write_task] ,  
    process = Process.sequential , # sequential or parallel 
    memory = True , 
    cache=  True , 
    max_rpm = 100 , 
    share_crew = True 
) 

print("Crew initialized successfully. Starting tasks...")

try:
    result = crew.kickoff (inputs = {
        'topic' : 'Artificial Intelligence in Healthcare' ,
        'channel' : '@krishnaik06'
    })
    
    print("Tasks completed successfully!")
    print("Result:")
    print(result) 
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc() 
