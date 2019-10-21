#!/bin/bash
. ../dockerSource.sh
docker stop yeadbot
docker rm yeadbot
docker run \
  -d \
  -v /home/raph/dockerRaph/githubstuff/dockershfiles/you-enter-a-dungeon:/discordbot:rw \
  --restart=always \
  --name=yeadbot \
  discordbot



# #!/bin/bash
# docker stop yeadbot
# docker rm yeadbot
# docker run \
#   --restart=always \
#   --name=yeadbot \
#   -v /home/raph/git/you-enter-a-dungeon:/discordbot:rw \
#   discordbot
