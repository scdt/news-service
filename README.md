
## Politota 
Service for posts and images.
### Vulnerabilities
* Flag inside in the image - real name(secret) is saved in "artist" exif file field. [Sploit](https://github.com/scdt/news-service/blob/main/sploits/politota/exif_image.py).
* Advisory msg replay: flags inside private posts. [Sploit](https://github.com/scdt/news-service/blob/main/sploits/politota/replay.py).
Для атаки нужно создать у себя в сервисе пользователя с таким же username, зарепортить, перехватить запрос от чекера на получение приватных постов и переслать его на атакуемый сервис.
### Deploy
```shell
cd service/politota
docker-compose up -d
```
Go to localhost:8080
