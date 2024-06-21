#!/bin/bash
dupe_script=$(ps -ef | grep "rclone-cron.sh" | grep -v grep | wc -l)

if [ ${dupe_script} -gt 2 ]; then
    echo -e "rclone sync script was already running."
    exit 0
fi
    echo -e "rclone sync start"
    date
    rclone sync remote:BRRES64_Data/Images /home/mzml/images/
    #rclone sync drive_iqa:BRRES64_Data/Images /home/pesquisa/images/
    docker cp /home/mzml/images/. 21eb83c42996:/app/images
    date
    echo -e "rclone sync end"
exit