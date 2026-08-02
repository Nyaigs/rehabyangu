#!/bin/bash
cd ~/rehabyangu && docker-compose exec -T backend python manage.py check_subscriptions
