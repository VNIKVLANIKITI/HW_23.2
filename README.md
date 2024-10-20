# HW_23.2
HW_23.2
# установка Redis
docker run -d --name redis -p 6379:6379 -p 
# проверка содержимого кэша
docker exec -it redis redis-cli
