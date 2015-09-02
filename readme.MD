## What is Rose&Dewdrop?
######Rose&Dewdrop 是一个基于tornado和zeromq的分布式websocket消息发布组建
* 其中rose构建于zeromq主要承担消息发布中心角色
* dewdrop构建于tornado并集成一个小型zeromq(PUB/SUB)发布中心
* rndsdk则承担选择最优rose节点并给rose节点下达消息发布作业的角色
![r&d_structure](rdstu.png)

## 为什么tornado节点不直接把websocket链接绑定到rose？

* 好处主要有两个
    *   如果直接把tornado的websocket链接直接绑定到rose，那么rose的压力会很大，假设3个tornado节点每个节点10万连接，那么rose就要承担30万连接
    *   另一个好处就是rose节点挂掉不会导致前端设备与tornado的连接中断，未来只需要恢复rose，前端可以无痛感知

##演示
######实例在demo中，先把dewdrop的serv.py跟rose的bloom.py跑起来，然后运行sdk中wand的test2，是一个每几十毫秒生成一条广播股价的服务

![demo_stock](stock.gif)
