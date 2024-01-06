请你用Python实现以下功能：

软件分为服务端与客户端
服务端有配置文件 config.json，包含配置项 "clientCacheTime" 和 "recordCacheTime"
服务端用Python的Flask框架实现，它监听所有IPV6连接，并且提供1个接口：
1）/route/sync，POST接口，有一个参数 "clientDomain" ，和一个可选的参数 "force"，参数通过 Json 格式传递，注意参数 "force" 是可选的，也就是说可能不出现，然后它读取客户端的 IPV6 地址，并将 Name 与 客户端 IPV6 地址的映射记录下来，同时还要记录最近的上报时间。之后遍历映射表，将上报时间超过 "recordCacheTime" 分钟的条目删除，其他条目则将 Name 与 IPV6 地址映射记录到 json 中，最后返回这个 json。针对每个相同的 "clientDomain"，你需要缓存上一次返回的映射表与返回时间，如果返回时间间隔少于 "clientCacheTime" 分钟，则返回空 json，表示不需要更新，但是，如果请求参数中 "force" 为 1，则无视缓存，必须返回映射表。你需要注意映射表的线程安全问题。


客户端：
客户端也使用 Python 实现。
客户端需要兼容 Linux 与 Windows，首先有一个配置文件 config.json，其中有配置项 "domain"，"syncTime"，"serverAddr"，"serverPort"，"domainSuffix"。客户端一直允许，每间隔 "syncTime" 秒，就向服务端的 /route/sync 发送请求，参数 "clientDomain" 为配置文件中的 "Domain"，当收到服务端返回后，如果为空 json，则结束，如果不是，则用服务端返回的映射关系修改本地的 host 文件，使得 Domain 能够映射到 IPV6 地址。注意，替换的过冲中，只要影响 host 文件中以 "domainSuffix" 为后缀的域名，不用修改其它域名的映射。
此外，当客户端首次启动的时候，需要发送一次 "force=true" 的 /route/sync 请求，以强制同步。
除此以外，你还要在Linux与Windows上分别提供一个启动脚本，将客户端程序设置为开机启动并且运行在后台守护进程。
客户端配置中还有2个参数 "gateway" 和 "networkInterface"，其中 "networkInterface" 为一个列表。如果 "gateway" 不为空，则在程序启动的时候，为所有的 "networkInterface" 中指明的网卡添加一个 IPV6 的默认网关 "gateway"，在 Windows 上，是如下的一行命令：
netsh interface ipv6 add route ::/0 interface="15" store=persistent aaaa::bbbb


请你给出服务端与客户端的代码，包括配置文件。