# jobtime

## Overview

jobtime is a tool to visualize job execution time for [Job Arranger](https://www.jobarranger.info/jaz/top.html).

![](output/joblog.svg)

## Features
- job execution times can be viewed at a glance
- colored by job status (success, failure, in time, overtime)

## Requirements
- Docker Engine
- Docker Compose
- Job Execution Log  
    - required: yes
    - how to get: 
        - [JobArranger Manager GUI](https://www.jobarranger.info/document/doku.php?id=4.0:operation:management:08file)
        - [jobarg_joblogput command](https://www.jobarranger.info/jaz/operation-manual_2.0/10external-joblogput.html)
    - encoding: UTF-8
    - newline code: LFs
- Job Schedule
    - required: no
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
    schedule.csv # if you need

# example 1.
docker exec -it jobtime python src/main.py --joblog=joblog.csv 
# --> output/joblog.svg

# example 2.
docker exec -it jobtime python src/main.py --joblog=joblog.csv --schedule=schedule.csv

# example 3.
docker exec -it jobtime python src/main.py --joblog=joblog.csv --schedule=schedule.csv --output=result.png
# --> output/result.png

```
## License
[MIT](https://choosealicense.com/licenses/mit/)

## Author
[gtk7032](https://github.com/gtk7032)