FROM python:3.6
MAINTAINER Raph Gallardo

WORKDIR /discordbot

RUN python -m pip install discord.py==0.16.12
RUN python -m pip install requests==2.20.0
RUN python -m pip install urllib3==1.24.1

RUN chmod 755 /discordbot

VOLUME ["/discordbot/"]

CMD ["python", "/discordbot/pyDiscordBot.py"]
