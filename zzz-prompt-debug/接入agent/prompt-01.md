### 需求01
写一个astrbot的插件，效果类似于云端的claudecode，通过qq对话的形式请求，在某一个工作目录下运行，有完整的claudecode的功能，比如skills，mcp，hooks，等
你可以参考这个项目：https://github.com/yihuineng/cc-ding.git，这个项目是接入dingding的
我已经clone到本地了：cc-ding
可以参考权限管理，架构，等，效果要是一样的，同时要有插件的便利性

### 需求2
1. 想要接入，codex，claudecode，opencode，还有别的agent，比如pi agent类似这样
2. 同时有一个白名单，就是群里面都可以和cc聊天，但是，不在白名单里面的用户，只有只读权限，并且是当前工作目录的只读权限，这个需要权限
3. 私聊的对话应该保存，或者说可以查询，可以回忆
   1. 比如可以类似qq一样翻聊天记录，岁月史书
4. 需要可以切换工作目录，获得不同的人设，或者不同的工作区间
5. 同时需要有授权的能力，一些危险操作需要授权，比如修改工作区以外的文件，执行危险脚本类似的
6. 管理员可以更换工作目录
7. 有一个基础的CLAUDE.md,AGENTS.md，基础的.codex/skills,.claude/skills,还有基本的hooks，settings，权限控制最好是上层控制，删除文件之类的

### 需求 3
1. 权限/目录
2. 你搜索一下，对于，claudecode，我是通过代码来调起cc的，就是这个agent代理如果要删除文件，修改文件，这个权限我能控制吗，还有沙箱，沙箱实际上是什么，用什么技术栈实现的，沙箱内部文件的删除，shell命令的执行，都是可以被控制的吗？
3. 
### 需求 4

1. 对于工作目录，你看下，这几个文件夹，同时包括worktree的文件夹，是目前被允许的，mine-blog，mine-interest，person-config，mine-interest.worktrees（这个文件夹下的所有worktree）这些文件夹都在/Users/mobius/Documents/111AAA-code，这个目录下面
2. 目前cd命令，就是有点不友好，能不能这样，加一个cd list命令，输出所有被允许的工作目录，然后，cd cd-list的目录序号然后就可以切换目录

### 需求5
1. 还是有点疑问，就是群内聊天的时候，guest和白名单，或者是，每一个群成员的对话是共享的吗？
2. 需要bot可以阅读图片，引用的消息，引用的图片，转发的消息，同时可以发送图片消息，图片加文字消息
3. github page更新的频率可以很频繁吗，用cc-qq改完代码，得到diff，就是代码dff生成一个html，然后上传到github page然后更新，这样让我好看一点，或者你看能不能用语雀mcp或者什么，反正就是代码diff又好的展示出来
   1. 其实就是我想很好的展示长文本，qq也不能渲染md
   2. 我在想其实长文本渲染成一个html挺好的的，或者限制一下输出

### 需求6
1. 或者这样，如果涉及发送图片，渲染html，html里面有图片，然后截图即可，感觉llm输出不可控，
   1. 简单来说如果本次新建了html就截图，然后发送即可
2. 感觉是不是不管什么回复，都渲染成html就挺好，解决了长文本，富文本，图片，发送的问题
3. 现在长文本渲染成html之后，发送，没有进入claude的上下文，感觉这个不是bug是正常现象
4. 写几个基本的skill
   1. 回复的文本，渲染成友好的html，然后截图，然后发送
   2. 绘图的skill
   3. 绘制svg，思维导图的skill
   4. html动画的skill（这个是需要上传到github page
5. 这个bot需要不同的人设，并且可以切换，不同人设的session不同
   1. 可以通过对应工作区的CLAUDE.md的替换实现
6. 写一个webui对于这个插件，对于每个群聊的工作区，工作区里面有哪些skill，mcp，
7. 现在转发消息也不能看，你看下这个插件的思路：integrations/astrbot/astrbot_plugin_sourcehub_inspector，或者阅读这个文档看一下开发过程：.devflow/multi-source-hub/NEXT-SESSION-PROMPT-multi-source-hub.md
8. 现在缓存
### 未来需求
1. 当长时间不对话，能不能检测当前正在输入这个状态，然后告诉用户，当前对话的上下文长度，根据什么时候创建的，如果太长时间之前创建的然后推荐用/new一个对话
2. 通过acp，或者对话数据的共享，实现并行？
3. 私聊的时候，短时间内多次消息，需要聚合成一条，比如30s，10s，1min，类似这样，然后私聊会保存聊天的上下文，超过限制自动截断（这个也能让codex/claudecode做，比如上下文压缩）
4. 可以发送语音消息，看看有没有现成的astrbot，或者dsh插件，可以参考一下