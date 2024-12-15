## Install
`python3 -m venv miniwallet`
`source miniwallet/bin/activate`
`pip install -r requirements.txt`

## Install My SQL
Create docker compose file
```
version: '3.3'
services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_DATABASE: 'miniwallet'
      MYSQL_USER: 'miniwallet'
      MYSQL_PASSWORD: 'miniwallet123'
      MYSQL_ROOT_PASSWORD: 'miniwallet123'
    ports:
      - '3306:3306'
    expose:
      - '3306'
    volumes:
      - my-db:/var/lib/mysql
# Names our volume
volumes:
  my-db:
```

Run this command
`docker compose up`

