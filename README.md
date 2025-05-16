# LotteryTask

# To run the project the requirements: 
- python 3.10+
- It's preferred a linux machine to add the script that would close and draw the lotteries at midnight to a crontab (can use equivalent cloud alternatives)
- docker compose
- for some linux distros follow the step in notes to allow docker to self initialize the DB the first spin up
- to execute the curl script use the following : python curl-util.py http://localhost:8000/lottery/v1/lottery/close