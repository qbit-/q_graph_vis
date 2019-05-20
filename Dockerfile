from node as build
workdir /qgraph

copy front/ .

RUN npm i
run npm run build

from python:3.6
expose 5000
copy --from=build qgraph /front
copy server/ server/

run ls
workdir /server
run pwd
RUN pip install --no-cache-dir -r requirements.txt
run mkdir output

cmd ["/bin/bash","start.sh"]
