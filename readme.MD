## What is Rose&Dewdrop?
######Rose&Dewdrop 是一个基于tornado和zeromq的分布式websocket消息发布组建
* 其中rose构建于zeromq主要承担消息发布中心角色(HUB)
* dewdrop构建于tornado并集成一个小型zeromq(PUB/SUB)发布中心
* rndsdk则承担选择最优rose节点并给rose节点下达消息发布作业的角色
![r&d_structure](rdstu.png)

* 疑问请联系(rowland.lan@163.com)

##架构设计
* dewdrop中tornado集成一个zeromq的PUB/SUB的迷你hub(使用ipc协议，实现为mmap)，每个websocket会绑定一个sub订阅这个本机hub
* 本机hub同时订阅所有的rose HUB节点，一旦rose HUB发布消息，本地迷你hub做一次转发
* rndsdk是用来给rose HUB下达消息作业的，采用蚁群算法确定最优节点

##什么是蚁群算法？
>各个蚂蚁在没有事先告诉他们食物在什么地方的前提下开始寻找食物。当一只找到食物以后，它会向环境释放一种信息素，信息素多的地方显然经过这里的蚂蚁会多，因而会有更多的蚂蚁聚集过来。假设有两条路从窝通向食物，开始的时候，走这两条路的蚂蚁数量同样多（或者较长的路上蚂蚁多，这也无关紧要）。当蚂蚁沿着一条路到达终点以后会马上返回来，这样，短的路蚂蚁来回一次的时间就短，这也意味着重复的频率就快，因而在单位时间里走过的蚂蚁数目就多，洒下的信息素自然也会多，自然会有更多的蚂蚁被吸引过来，从而洒下更多的信息素。因此，越来越多地蚂蚁聚集到较短的路径上来，最短的路径就找到了。


##简化版实现
* 在此地，为了简化这个模型，并没有专门为信息素建模。蚂蚁则是请求，每一只蚂蚁就是一个ping的req，直到回来，这条路径的信息素则+1
* 然后派出的蚂蚁会按照路径中的信息素量按比例随机选择路径
* 活动持续一段时间之后确立最优解
* 活动周期性的需要把每条路径信息素清0，因为如果某一条路径上信息素已经高达10000了，对信息素就不敏感了

## 为什么tornado节点不直接把websocket链接绑定到rose？

* 好处主要有两个
    *   如果直接把tornado的websocket链接直接绑定到rose，那么rose的压力会很大，假设3个tornado节点每个节点10万连接，那么rose就要承担30万连接
    *   另一个好处就是rose节点挂掉不会导致前端设备与tornado的连接中断，未来只需要恢复rose，前端可以无痛感知

##演示
######实例在demo中，先把dewdrop的serv.py跟rose的bloom.py跑起来，然后运行sdk中wand的test2，是一个每几十毫秒生成一条广播股价的服务

![demo_stock](stock.gif)
![demo_brush](cvb.gif)
