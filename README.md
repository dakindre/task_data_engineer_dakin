# Data Engineering Task


## Data Storage Design

### Question 1
##### How would you structure/represent the data?
The image below is a sample JSON grower_mission_feedback item injested in a NoSQL DB, which in this case is MongoDB. I chose this as the first step in the proccess to represent how JSON data with dynamic structure could be added added in a DB. The structure is based on a three part hierarchy as described below. 

Level 1: Constant Variables
These are keys value pairs that should in theory be included in each JSON file such as grower_mission.id and grower_mission.assigned_to and grower_mission.created_at. Of course this is only a sample of which fields might be included here. 

Level 2: Dynamic harvest Data
This level divides 



#### How would you make sure it is scalable if the data being retrieved changes?
#### Strengths/Drawback

### How would you expose this data to users (who use SQL)?

### What would you change from this process, if you had the chance to do so?
The most glaring issue I have with this process is the fact that it relies on a JSON file. When you said, "The Growers see the grower missions in the GrowerApp in order to fulfill their daily tasks, as well as report back all sorts of data regarding the harvest" I would envision a more advanced approach to data capture. Similar to how tracking on a website is implemented you could invoke an API when the grower mission is updated passing all the relevant data as parameters. This could be done through a streaming pipeline or just by simply invoking an API to a FAAS. 

![alt_text](/images/ontology_raw.PNG)

## Table of Contents

