# Data Engineering Task

## Task 1


### How would you structure/represent the data?How would you make sure it is scalable if the data being retrieved changes?Strengths/Drawback

The image below is a sample JSON grower_mission_feedback item injested in a NoSQL DB, which in this case is MongoDB. I chose this as the first step in the proccess to represent how JSON data with dynamic structure could be added into a DB. The structure is based on a three part hierarchy as described below. The implementation of course assumes certain design decisions made within the application itself which is in of itself a drawback. This implementation also involves having MongoDB. I assumed that there was already a production DB that could simply add a new collection to. Another downside to this approach is that you have an array of an array. When developing the ETL for this you would quickly find that you cannot have an array of an array in a DWH. Therefore a restructuring and unnesting would need to be done during the ETL process.


#### Level 1: Constant Variables
These are keys value pairs that should in theory be included in each JSON file such as grower_mission.id, grower_mission.assigned_to and grower_mission.created_at. Of course this is only a sample of which fields might be included here. 


#### Level 2: Dynamic harvest Data
This level breaks down the mission by farming_unit, column, tray, and growth_stage. I did it this way to accomodate the possibility of having multiple farming units under one mission. Because we don't know what farming unit or how many might be used during the mission it's structured in an array. Each array contains data about the specific farming unit broken down by (farming_unit_id, column, tray, growth_stage). One drawback of this granularity is that it may create too many array elements. It could also be reduced to fewer columns.

#### Level 3: Dynamic task Data
The third level represents the "tasks" belonging to the farming_units. Again this is structured in an array to accomodate the unknown number of tasks belonging to any particular farming_unit. The example structure is (name, type, description, logged_at). Of course there may be a need for more fields but for the purposes of this example I think it's sufficient. As you can see in the example the name and type field refer to any number of actions relating to the farming_unit_id. The idea would be that these are based on logic within the application where a category is selected such as note or harvest. As that category list grows on the app however this array structure could accomodate. You wouldn't need to modify anything on the back-end.


![alt_text](/images/Infarm.png)


### How would you expose this data to users (who use SQL)?

I invision that there would be a batch ETL process that runs regularly against the DB. Maybe a daily process. The nice feature as I've learned to using arrays in DBs is that the ETL schema would not need to be altered each time a new item was created. The ETL process would then write out to BigQuery using the same array structure. Of course there is an assumed knowledge of knowing how to UNNEST the data but ultimately people profficient in SQL could gain insight about specific information relating to farming_units on a mission level.

### What would you change from this process, if you had the chance to do so?
The most glaring issue I have with this process is the fact that it relies on a JSON file. When you said, "The Growers see the grower missions in the GrowerApp in order to fulfill their daily tasks, as well as report back all sorts of data regarding the harvest" I would envision a more advanced approach to data capture. Similar to how tracking on a website is implemented you could invoke an API when the grower mission is updated passing all the relevant data as parameters. This could be done through a streaming pipeline or just by simply invoking via API a FaaS.




## Task 1

