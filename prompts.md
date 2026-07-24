# 人物风格转换 Prompt 库（FLUX.2 klein 图生图）

## 怎么用

```bash
python3 gen.py "<下面任选一条>" out.jpg --img 你的照片.jpg
```

## 核心原理（必读，决定成败）

FLUX.2 klein 的图生图是**指令式参考编辑**,不是传统 img2img:

- **没有 strength 旋钮**。变化幅度全靠 prompt 措辞。
- **指令里必须写明"保留什么"**(脸/身份/发型/姿势/构图),否则人物会跑样、换脸。
- prompt 是**祈使句指令**("把这个人变成…"),不是场景描述("一张…的照片")。
- 英文最稳;中文也能用(编码器是 Qwen3),想试就把指令换成中文。

**通用模板:**
> `Transform this person into [风格]. Keep their facial features, identity, hairstyle, pose, and overall composition. [风格细节].`

调节变化幅度:
- 想**更像原图** → 加 `preserve the exact facial features and identity`
- 想**更大胆** → 把 preserve 那句删掉,或开头改成 `Reimagine this person as…`
- 想**更轻** → 风格词前加 `subtle / light`;**更重** → 加 `strong / heavy, fully restyled`

---

## 风格清单（直接复制）

**1. 日系动漫 Anime**
`Transform this person into a Japanese anime character: clean cel-shaded linework, large expressive eyes, flat vibrant colors, soft anime shading. Keep their identity, hairstyle, pose, outfit and composition.`

**2. 吉卜力 水彩 Ghibli**
`Repaint this person in Studio Ghibli hand-painted watercolor style: soft pastel palette, gentle painterly shading, warm storybook atmosphere. Keep their face, pose and composition recognizable.`

**3. 皮克斯 3D Pixar**
`Render this person as a Pixar-style 3D animated character: smooth subsurface-scattering skin, big friendly eyes, soft cinematic lighting, slightly stylized proportions. Preserve their identity, expression and pose.`

**4. 古典油画 Oil painting**
`Repaint this person as a classical oil portrait: visible thick brushstrokes, rich impasto texture, Rembrandt-style chiaroscuro lighting on canvas. Keep the likeness, pose and composition.`

**5. 赛博朋克 Cyberpunk**
`Restyle this person as a cyberpunk character: teal-and-magenta neon rim lighting, rainy futuristic city bokeh behind, subtle cybernetic details, cinematic. Preserve their face, pose and framing.`

**6. 黏土定格 Claymation**
`Turn this person into a claymation stop-motion character: handcrafted polymer-clay texture with visible fingerprints, soft studio lighting, Aardman style. Keep their identity, expression and pose.`

**7. 16位像素 Pixel art**
`Convert this person into 16-bit pixel art: limited retro palette, crisp dithered shading, game sprite look. Preserve the pose, outfit colors and recognizable features.`

**8. 水墨国风 Chinese ink**
`Repaint this person as a traditional Chinese ink-wash painting (shui-mo): flowing black brushstrokes, minimal color, rice-paper texture, generous negative space. Keep the pose and likeness.`

**9. 美式漫画 Comic**
`Redraw this person as an American comic-book hero: bold ink outlines, halftone dot shading, dramatic cross-hatching, saturated colors. Preserve identity, pose and composition.`

**10. 乐高 LEGO**
`Rebuild this person as a LEGO minifigure: glossy plastic, cylindrical printed-face head, blocky C-shaped hands, visible studs, toy-photography lighting. Keep the recognizable outfit colors and pose.`

**11. 铅笔素描 Pencil sketch**
`Convert this person into a detailed graphite pencil sketch: fine cross-hatching, soft shading, white paper, hand-drawn. Preserve the likeness, expression and pose.`

**12. 证件照 → 职业写真（同人不同风，偏写实）**
`Restyle this casual photo into a professional studio headshot: clean grey backdrop, soft key light, sharp business attire. Keep the exact same face, identity and hairstyle.`
