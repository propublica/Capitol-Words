FROM python:3.6-slim

RUN mkdir -p /mnt/capitolwords
WORKDIR /mnt/capitolwords

# first two are for python, last five are for node
RUN apt-get update && \
    apt-get install -qq -y build-essential libpq-dev --no-install-recommends && \
    apt-get install -y curl && \
    apt-get install -y gnupg && \
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

COPY . /mnt/capitolwords

# RUN python manage.py clears3staticfiles
# RUN python manage.py collectstatic --no-input --clear
# RUN python manage.py migrate

EXPOSE 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "capitolweb.wsgi -p capwords.pid -D"]
