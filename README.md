# jobtime

## Overview

jobtime is a tool to visualize job execution time for [Job Arranger](https://www.jobarranger.info/jaz/top.html).

![](output/joblog.svg)

## Features

- job execution times can be viewed at a glance
- colored by job status (success, failure, on time, over time)

## Requirements
- Docker Engine
- Docker Compose
- job execution log  
    - how to get: 
        - [JobArranger Manager GUI](https://www.jobarranger.info/document/doku.php?id=4.0:operation:management:08file)
        - [jobarg_joblogput command](https://www.jobarranger.info/jaz/operation-manual_2.0/10external-joblogput.html)

    - required
    - encoding: UTF-8
    - newline code: LF
    
- job Schedule file (if you need)
    - see [sample](resources/schedule.csv)
    - encoding: UTF-8
    - newline code: LF

## Download

```bash
git clone https://github.com/gtk7032/jobtime.git
```

## Usage

```bash

cd jobtime

docker-compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)

ls resources
    joblog.csv
# schedule.csv (maybe)

# example 1.
docker exec -it jobtime python src/main.py --joblog=joblog.csv 

# example 2.
docker exec -it jobtime python src/main.py --joblog=joblog.csv 
--schedule=schedule.csv

# example 3.
docker exec -it jobtime python src/main.py --joblog=joblog.csv 
--schedule=schedule.csv
 --output=result.png

 ls output
```
## License

[MIT](https://choosealicense.com/licenses/mit/)

## Author
[gtk7032](https://github.com/gtk7032)