# Data Engineering Task

## Task 1


### How would you structure/represent the data?How would you make sure it is scalable if the data being retrieved changes?Strengths/Drawback

The image below is a sample grower_missions document from the JSON file. For the purposes of this example I modeled it in MongoDB. Due to the schemaless nature of noSQL DB's not every document has to adhere to the same structure. However it is best practice to try and capture data in a similar fashion. I detail below how I would approach this topic. The data hierarchy I've provided is split into three levels. Of course this assumes a certain app design structure to be in place but allows for scalability in it's use of arrays.

#### Level 1: Constant Variables
These are keys value pairs that should in theory be included in each JSON file such as grower_mission.id, grower_mission.assigned_to and grower_mission.created_at. Of course this is only a sample of which fields might be included here. 


#### Level 2: Dynamic harvest Data
This level breaks down the mission by farming_unit, column, tray, and growth_stage. I did it this way to accomodate the possibility of having multiple farming units under one mission. Because we don't know what farming unit or how many might be used during the mission it's structured in an array. Each array contains data about the specific farming unit broken down by (farming_unit_id, column, tray, growth_stage). One drawback of this granularity is that it may create too many array elements. It could also be reduced to fewer columns.

#### Level 3: Dynamic task Data
The third level represents the "tasks" belonging to the farming_units. Again this is structured in an array to accomodate the unknown number of tasks belonging to any particular farming_unit. The example structure is (name, type, description, logged_at). Of course there may be a need for more fields but for the purposes of this example I think it's sufficient. As you can see in the example the name and type field refer to any number of actions relating to the farming_unit_id. The idea would be that these are based on logic within the application where a category is selected such as note or harvest. As that category list grows on the app however this array structure could accomodate. You wouldn't need to modify anything on the back-end.


![alt_text](/images/Infarm.png)


### How would you expose this data to users (who use SQL)?

There are several approaches that would work here but for the purposes of addressing data warehousing I'll choose that. An ETL pipeline could be developed to run at a specified frequency in which you extract the data from mongo, apply transformations (reducing the nesting level. Cannot have arrays of arrays in BQ), and ultimately writing out to BQ appending to a historical table to gain insight of the evolution of missions over time.

### What would you change from this process, if you had the chance to do so?
I find the reliance on a JSON file to be annoying. I would instead find a scalable way to write data directly from application to DB. It's then accessible for any number of applications that pull from Mongo. I am not a huge fan of data lakes as I think they end up being very poorly managed.




## Task 1

