FROM python:3.6-slim

RUN mkdir -p /mnt/capitolwords
WORKDIR /mnt/capitolwords

# first two are for python, last five are for node
RUN apt-get update && \
    apt-get install -qq -y build-essential libpq-dev --no-install-recommends && \
    apt-get install -y mysql-server && \
    apt-get install -y default-libmysqlclient-dev && \
    apt-get install -y curl && \
    apt-get install -y gnupg && \
    apt-get install -y nginx && \
    apt-get install -y supervisor && \
    apt-get -y autoclean && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash -

RUN apt-get update && apt-get install -y \
        gcc \
        gettext \
        sqlite3 \
        nodejs \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*


RUN npm -g install yuglify
RUN npm build

COPY requirements.txt /mnt/capitolwords
RUN pip3 install --no-cache-dir -r requirements.txt

# After pip runs we need to download the spacy english model for the parser to work
RUN python -m spacy download en

COPY . /mnt/capitolwords

# RUN python manage.py clears3staticfiles
# RUN python manage.py collectstatic --no-input --clear
# RUN python manage.py migrate

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY capwords-nginx-config.conf /etc/nginx/sites-available
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/capwords-nginx-config.conf /etc/nginx/sites-enabled

COPY capwords-app.conf /etc/supervisor/conf.d/

WORKDIR /mnt/capitolwords/capitolweb

EXPOSE 80
CMD ["supervisord", "-n"]
