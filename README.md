# Data Engineering Task

## Task 1


### How would you structure/represent the data?How would you make sure it is scalable if the data being retrieved changes?Strengths/Drawback

The image below is a sample grower_missions document from the JSON file. For the purposes of this example I modeled it in MongoDB. Due to the schemaless nature of noSQL DB's not every document has to adhere to the same structure. However it is best practice to try and capture data in a similar fashion. I detail below how I would approach this topic. The data hierarchy I've provided is split into three levels. Of course this assumes a certain app design structure to be in place but allows for scalability in it's use of arrays.

#### Level 1: Constant Variables
These are key value pairs that should in theory be included in each JSON file such as grower_mission.id, grower_mission.assigned_to and grower_mission.created_at. Of course this is only a sample of which fields might be included here. 


#### Level 2: Dynamic harvest Data
This level breaks down the mission by farming_unit, column, tray, and growth_stage. I did it this way to accomodate the possibility of having multiple farming units under one mission. Because we don't know what farming unit or how many might be used during the mission it's structured in an array. Each array contains data about the specific farming unit broken down by (farming_unit_id, column, tray, growth_stage). One drawback of this granularity is that it may create too many array elements. It could also be reduced to fewer columns.

#### Level 3: Dynamic task Data
The third level represents the "tasks" belonging to the farming_units. Again this is structured in an array to accomodate the unknown number of tasks belonging to any particular farming_unit. The example structure is (name, type, description, logged_at). Of course there may be a need for more fields but for the purposes of this example I think it's sufficient. As you can see in the example the name and type field refer to any number of actions relating to the farming_unit_id. The idea would be that these are based on logic within the application where a category is selected such as note or harvest. As that category list grows on the app however this array structure could accomodate. You wouldn't need to modify anything on the back-end.


![alt_text](/images/Infarm.png)


### How would you expose this data to users (who use SQL)?

There are several approaches that would work here but for the purposes of addressing data warehousing I'll choose that. An ETL pipeline could be developed to run at a specified frequency in which you extract the data from mongo, apply transformations (reducing the nesting level. Cannot have arrays of arrays in BQ), and ultimately writing out to BQ appending to a historical table to gain insight of the evolution of missions over time.

### What would you change from this process, if you had the chance to do so?
I find the reliance on a JSON file to be annoying. I would instead find a scalable way to write data directly from application to DB. It's then accessible for any number of applications that pull from Mongo. I am not a huge fan of data lakes as I think they end up being very poorly managed.

## Task 2

The dag file I created to complete this assignment can be found in the /dag folder. The output is available in this [google sheet](https://docs.google.com/spreadsheets/d/1nqMmNdDHQFyNrqhYTjvISKaeCxZAskZUHbWH509vfW0/edit?usp=sharing) . I've subdivided this into three parts:

1. Results
2. Dynamic Dags
3. Code Explanation


### Results
The file contains two complete runs(By organization) of the ~900 items created in Zoho Warehouse. Due to limitation of the trial membership and warnings from Zoho about API limits I only ran it for two organization. The file contains API data related to dynamic creation of (organizations, item list collection, item creation, item updates). Below are two examples of a few of those. You can look through the file for the others. The last image shows the result of the run in zoho inventory UI.

![alt_text](/images/org_creation.PNG)
![alt_text](/images/item_creation.PNG)
![alt_text](/images/output_sample.PNG)
![alt_text](/images/zoho_warehouse_items.PNG)

### Dynamic Dags
The dags were created dynamically based on the organizations that were in the "Zoho Warehouses" tab. You can see in the Airflow UI the different dags with the org_id acting as the dag_id. There is a further explanation of how I constructed this in the code. Below are some sample images

![alt_text](/images/zoho_dags.PNG)
![alt_text](/images/dag_task.PNG)

### Code Explanation
Below is an explanation of the different sections of the code divided into three main parsts (API, Google Read/Write, Dag Factory)

#### Zoho API
The API code section allows for 5 main functions. One limitation I ran into was the get_items_list function does not return a full list of the existing items in the org. Therefore the matching for determining whether to update or create doesn't always result in the correct operation. Due to time constraints I did not look further into the issue. 

1. [get_org](https://github.com/dakindre/infarm/blob/23951c630c04b70a485586b7b6481d0dc98524df/dags/zoho.py#L52): gets the org_id using org_name
2. [create_org](https://github.com/dakindre/infarm/blob/23951c630c04b70a485586b7b6481d0dc98524df/dags/zoho.py#L61): created a new organization if it doesn't exist and set org_id
3. [get_items_list](https://github.com/dakindre/infarm/blob/23951c630c04b70a485586b7b6481d0dc98524df/dags/zoho.py#L107): retrieve items belonging to the specified org
4. [create_item](https://github.com/dakindre/infarm/blob/23951c630c04b70a485586b7b6481d0dc98524df/dags/zoho.py#L134): creates a new item in the specififed org
5. [update_item](https://github.com/dakindre/infarm/blob/23951c630c04b70a485586b7b6481d0dc98524df/dags/zoho.py#L115): updates a specified item within the org

#### Dynamic Dags
The code to dynamically generate dags can be found [here](https://github.com/dakindre/infarm/blob/23951c630c04b70a485586b7b6481d0dc98524df/dags/zoho.py#L185). It's very simple to understand. The dags are generated based on the org_id as mentioned above. The use of `globals()[f'zohowarehouse_{org_id}'] ` allows a dynamic variable to be set and generates a unique dag for each org. 

#### Google Functions
The google functions are just the way of extracting data from the google sheet and writing the output to. If you'd like to test this you could put your own service account credentials in a config folder. 

## Task 3

#### Diagram

The diagram below outlines my general approach to a semi real-time infrastructure in AWS. The task specified that the request and demands of teams are likely to change over time. In order to accomodate different demands for the data the key component is in the IoT topic/rule definitions. You can subscribe/unsubsribe to topics as needed to gain insight. The IoT rules then are the determinant service for how the data is further processed and which services are used. Including new rules opens up new avenues of data processing and exposure. This approach is easy to maintain and scalable from within the console. Very little coding is needed within the IoT core to accomplish these tasks. The IoT analytics core can use data from a multitude of sources. In this example we just connect it with the IoT core. 


The diagram shows as an example three different rules all with different service destinations. Those rules are explained below

##### Rule #1
The first pipeline is intended to capture and store semi-raw data. I've included a lambda function in there in case some preprocessing should be done for long term storage. I chose to include this because many times stakeholders will come with requests to analyze historical data. S3 storage can be archived at low costs and eventually removed if needed. This is more of a safeguard process in case you need to reference older data.

##### Rule #2
The second pipeline is intended for analysis. This process services both analysts and data scientists. Essentially it utilizes the AWS IoT Analytics service core (channels, pipelines, data stores, data sets, and notebook). This is a very easy to understand and fully scalable system. I will not go into detail about each sub-service but will elaborate on the additional services I've included. After the pipeline a lambda function is invoked. This essentially is the cleaning portion of the pipeline. The data can be standardized and filtered. Additionally certain triggers could be added in the lambda for anomoly detection and error handling. The data is then stored in S3 which acts as the data store for our purposes. This could be either a S3 bucket created by the analytics service or one already in existence. The datasets using the data store source are then referenced by a reporting tool (quicksight in this example) or the jupyter notebooks which can be used by data scientists to analyze a series of events. 

##### Rule #3
The third pipeline simply writes the data to AWS message queue service. Each message invokes a lambda function which can then process the data and write it to any number of sources that the software team would need.

![alt_text](/images/Task3.png)

#### Question 2: Explain choices/caveats of other systems and reason the choice
I chose this approach because I've found that cloud services are highly performant and scalable in contrast to custom pipelines. They are also much easier (typically) to provision and deploy. I am not an expert in IoT processes so I chose a fairly standard approach here. One problem with this approach is that potentially you store redundant data. That can become expensive quickly. I would have instead like to choose a system that has a single source of truth and then build various pipelines off of that. Although I think given the design of IoT cores and rules the intention is to split the pipelines at this point. At least that was my understanding. 


#### Question 3: How would you structure the code? What would you implement to ease development effort?
I think the implementation speaks for itself in terms of code complexity. The core coding components would reside within the lambda function themselves. The logic there would be specific to the use cases of the data. For example for software you would need to format the data in a way that is usable for them within the lambda before publishing. Each lambda would be invoked via API and would be integrated with a CI/CD (CircleCI) tool so that you could make modifications immeadiately to the pipeline.


#### Question 4: How do you envision the long term maintenance?
The maintenance required to expand and maintain the pipelines would be quite easy. Due to the wide varieties of services that IoT core can connect with any new pipeline can be built from that block. Because Infarm uses a similar approach to sensors (assumed) in each module the number of rules and topics would be relatively easy to maintain after initial development. 
