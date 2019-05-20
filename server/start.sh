mkdir mnt
echo copying files
cp -r /front/* /mnt/
python -u web_server/server.py
