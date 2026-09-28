### 需求01
写一个astrbot的插件，效果类似于云端的claudecode，通过qq对话的形式请求，在某一个工作目录下运行，有完整的claudecode的功能，比如skills，mcp，hooks，等
你可以参考这个项目：https://github.com/yihuineng/cc-ding.git，这个项目是接入dingding的
我已经clone到本地了：cc-ding
可以参考权限管理，架构，等，效果要是一样的，同时要有插件的便利性

### 需求2
1. 想要接入，codex，claudecode，opencode，还有别的agent，比如pi agent类似这样
2. 同时有一个白名单，就是群里面都可以和cc聊天，但是，不在白名单里面的用户，只有只读权限，并且是当前工作目录的只读权限，这个需要权限