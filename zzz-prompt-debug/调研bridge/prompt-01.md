### 需求1
https://github.com/Derpyu520/qq-bridge
https://github.com/Yuuyuko-uu/dsh-qq-bridge
https://github.com/h-D-ACE/dsh-qq
https://github.com/xcisxc29/dsh-qq-plugin
https://github.com/beiheng127/dsh-dfy-qq
https://github.com/miku05231/DSH-Fatwhale-QQ
这是我找的，dsh接入qq的插件，你对比一下，我现在写的cc_qq插件，和我借鉴cc-ding的插件，看看有什么可以借鉴的地方吗，这几个dsh接入原理大致是什么，你先把代码clone下来到zzz-prompt-debug/调研bridge，新建一个文件夹，clone这些代码，然后添加到gitignore，这些代码不用提交，最后给我一个详细的调研文档
### 需求2
最近应该还调查了一下qq官方的dsh插件：https://github.com/tencent-connect/dsh-qqbot；
另外你看下astrbot的这个插件：https://github.com/Him666233/astrbot_plugin_group_chat_plus，原理大概是什么；
再次集思广益一下；
1. 我有一个想法：我发现我写的插件，是一个中间层，napcat把收到的消息给astrbot，cc-qq这个插件，把消息给代理（claude or codex），然后代理返回消息，一层一层的回传
   1. 这样会出现，发送富文本会出问题，比如发送图片加文字，发送视频，发送纯文本是没有问题的
   2. 我想对于代理，写一个插件，或者别的什么，让它可以安装规定形式输出消息，然后我做转化，就配置openai responses协议一样
   3. 然后就可以很好的发送图片，或者图文并茂
2. 你看下这几个，仓库，还有cc-ding，有做类似的操作吗？还是接入dingding的时候，是符合dingdingbot的协议的，还有官方的qqbot，发送消息的时候，也是有一定的协议规定的
3. 主要就是我做的是中转这个操作，不是自己从零写一个agent，借用了agent的功能
4. 你看下，这个官方的qqbot的插件https://github.com/tencent-connect/dsh-qqbot，
   1. 它默认的权限管理是什么？我在设置页面没有看到，但是应该是有的，它是如何做到的？你看下还有就是如何做到审批的，还有标准的格式，还能渲染md
   2. 看看napcat这种用三方的qqbot可以做到吗？
   3. 还有一个疑问，qqbot可以获取到转发的多层消息吗？