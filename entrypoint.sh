#!/bin/bash
export $(id)
echo "default:x:$uid:0:user for teletgram_bot_dev:/opt/telegram_bot:/bin/bash" >> /etc/passwd
python3.11 /opt/telegram_bot/main.py