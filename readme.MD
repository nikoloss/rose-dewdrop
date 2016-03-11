## Notice
###### The project is temporary under reconstruction

##注意
###### 此项目目前处于大规模重构当中,预计完工预期3.14日

## What is Rose&Dewdrop?
######Rose&Dewdrop 是一个基于tornado和zeromq的分布式websocket消息发布组件
* 其中rose构建于zeromq主要承担消息发布中心角色(HUB)
* dewdrop构建于tornado并集成一个小型zeromq(PUB/SUB)发布中心
* rndsdk则承担选择最优rose节点并给rose节点下达消息发布作业的角色
![r&d_structure](rdstu.png)

* 疑问请联系(rowland.lan@163.com)

##架构设计
* dewdrop中tornado集成一个zeromq的PUB/SUB的迷你hub(使用ipc协议，实现为mmap)，每个websocket会绑定一个sub订阅这个本机hub
* 本机hub同时订阅所有的rose HUB节点，一旦rose HUB发布消息，本地迷你hub做一次转发
* rndsdk是用来给rose HUB下达消息作业的，采用蚁群算法确定最优节点


## 为什么tornado节点不直接把websocket链接绑定到rose？

* 好处主要有两个
    *   如果直接把tornado的websocket链接直接绑定到rose，那么rose的压力会很大，假设3个tornado节点每个节点10万连接，那么rose就要承担30万连接
    *   另一个好处就是rose节点挂掉不会导致前端设备与tornado的连接中断，未来只需要恢复rose，前端可以无痛感知

##演示
######实例在demo中，先把dewdrop的serv.py跟rose的bloom.py跑起来，然后运行sdk中wand的test2，是一个每几十毫秒生成一条广播股价的服务，然后在浏览器中打开index.html看效果。

![demo_brush](cvb.gif)
![demo_stock](stock.gif)

