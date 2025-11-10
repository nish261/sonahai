#!/bin/bash
source venv/bin/activate

python complete_pipeline.py 500 1000 "ALL" 10 30 "AWS/S3,AWS/Elastic Beanstalk,Azure,Digital Ocean,WordPress.com"
