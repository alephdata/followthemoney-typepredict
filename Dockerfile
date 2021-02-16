FROM alephdata/followthemoney

LABEL org.opencontainers.image.title "FollowTheMoney type prediction ML tools"
LABEL org.opencontainers.image.licenses MIT
LABEL org.opencontainers.image.source https://github.com/alephdata/followthemoney-typepredict


COPY . /opt/typepredict
RUN pip install --no-cache -q -e "/opt/typepredict[analysis]"