# websocket集群
## websocket_server
基于Tornado的一个简易聊天室，支持websocket集群部署，利用rabbitmq和redis保证集群内的数据同步
[点击查看](websocket_server/README.md)

## backgroud_server
配合websocket_server使用，利用rabbitmq来处理一些业务，保证各节点数据同步
[点击查看](background_server/README.md)
