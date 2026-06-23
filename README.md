# 公众号封面 Codex Skill

一个用于生成微信公众号封面的 Codex skill：输入一张主视觉海报，先通过提示词生成两张新的封面设计稿，再拼接成一张 `3.35:1` 横版封面。

## 能做什么

- 从海报生成 `2.35:1` 主封面设计
- 从海报生成 `1:1` 缩略封面设计
- 自动拼接为 `3350x1000` 的最终公众号封面
- 严格匹配原海报配色、亮度、饱和度
- 默认只交付最终拼接图，不暴露中间图

## 安装

把 `gongzhonghaofengmian/` 文件夹复制到你的 Codex skills 目录：

```bash
cp -R gongzhonghaofengmian ~/.codex/skills/
```

然后在 Codex 中调用：

```text
用 $gongzhonghaofengmian，把这张海报通过提示词生成 2.35:1 和 1:1 两张公众号封面，再拼接成最终横图
```

## 输出规格

- 最终图：`3350x1000`
- 左侧主封面：`2350x1000`
- 右侧缩略封面：`1000x1000`
- 最终比例：`3.35:1`

## 设计原则

这个 skill 不把竖版海报直接裁成横图。正确流程是：

1. 参考原海报的风格、标题、配色和主视觉
2. 生成一张新的 `2.35:1` 主封面
3. 生成一张新的 `1:1` 缩略封面
4. 用脚本拼接两张生成图

## 手动拼接

如果你已经有两张封面图，可以直接使用脚本：

```bash
python gongzhonghaofengmian/scripts/create_wechat_cover.py \
  /path/to/left-2350x1000.png \
  --right-source /path/to/right-1000x1000.png \
  --output /path/to/final-cover.png
```

需要 Pillow：

```bash
pip install Pillow
```

## License

MIT
