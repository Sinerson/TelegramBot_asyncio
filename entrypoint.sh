#!/bin/bash
#export $(id)
#echo "default:x:$uid:0:user for teletgram_bot_dev:/opt/telegram_bot:/bin/bash" >> /etc/passwd
redis-server /opt/telegram_bot/redis.conf
python3.11 /opt/telegram_bot/main.py