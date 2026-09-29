### 需求
1. 可以写一个hooks，检查这个代理脚本是否启动，避免出现问题（这个暂时不用，暂定
2. 当agent回复完之后，hooks不是触发了吗，自定义一个tui，![alt text](images_md/image.png)就是比如类似这样如图所示，实际model:xxxx

第 2 条已由 Stop 钩子的 `systemMessage` 实现，文案是 `实际 model: ...`。第 1 条仍暂不实现。