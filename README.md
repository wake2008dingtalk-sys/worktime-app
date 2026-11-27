# WorkTime · 个人工时打卡

<!-- AUTO:VERSION -->
> **当前版本 v1.1.71**（versionCode 245）· 构建于 2026-11-27
<!-- /AUTO:VERSION -->


定位签到 + 工时统计。**Android APK**（Capacitor 套壳单文件页）与 **微信小程序**（云开发）共用一套数据与算法。

网页版：https://wake2008dingtalk-sys.github.io/worktime-app/

---

## 当前版本

| 项目 | 版本 | 说明 |
|---|---|---|
| APK | **v1.1.57** | versionCode 228 · 启动页 1080P 视频（首次 3.54s / 之后 2.5s） |
| Service Worker | `worktime-v45` | 改动页面后必须同步 +1，否则老缓存不更新 |
| 小程序 | **1.1.57** | 已上传，含「假期 N 天」显示 |
| 云函数 | `sync` / `updateSettings` / `updateRecord` / `clearRecords` | 见 `云函数补丁-可选/` |

构建产物：GitHub Actions → artifact `worktime-release-signed` → `worktime-release.apk`（已签名）。

---

## 仓库结构

```
index.html            单文件主体（页面 + 样式 + 逻辑，约 7000 行）
sw.js                 Service Worker，CACHE_NAME 需随版本递增
intro.mp4             启动页视频（1080×1920，3.3MB）
intro-poster.jpg      启动页海报帧（同时以 base64 内联进 index.html 做零延迟兜底）
city-bg.jpg           全 App 三维等距城市背景（110KB）
icon-1024/512/192.png 应用图标（由 make_icon.py 程序化生成）
make_icon.py          图标生成脚本（改颜色/指针角度改这里）
manifest.json         PWA 清单
privacy.html terms.html
cloudfunctions/       云函数源码
.github/workflows/    APK 构建流水线
```

---

## 几条硬约束（改之前必看）

1. **`APP_VERSION` 与 `CACHE_NAME` 必须一起升**。只改页面不升 SW 版本，用户会一直看到旧缓存。
2. **`const` 声明顺序是硬约束**。曾因 `SYNC_FG_MS` 写在 `initCloudSync()` 之后，导致绑定后每次启动 TDZ 报错、CloudSync 永不挂载。
3. **大段 HTML 改动后必须做结构自检**（div 平衡 + 深度扫描）。曾因多一个 `</div>` 把滚动容器提前关掉，设置页三组内容掉到顶层。
4. **注释里不要写闭合标签字面量**（如 `</div>`），会污染结构计数导致自检误报。
5. **关键 UI 不能静默失败**：未挂载 / 渲染异常 / 存储满都要能在「诊断」行看到。
6. **两端算法必须对同一批数据跑一遍**（`testbed/test_mp_v1125` 对比表），否则会出现 APK 10.8h、小程序 11.0h。

---

## 本地验证

```bash
cd testbed
node test_v1155.mjs        # 假期勾选
node test_v1142.mjs        # 启动页视频
node smoke_render_v1117.mjs # 渲染冒烟（抓 TDZ、未挂载）
```

`testbed/` 不在本仓库内，属于本地工作区。

---

## 最近变更

| 版本 | 内容 |
|---|---|
| v1.1.57 | 假期同步加独立时间戳 `holidaysUpdatedAt`，不被整体设置覆盖 |
| v1.1.56 | 假期标记纳入云同步；小程序端显示「假期 N 天」 |
| v1.1.55 | 统计页「☑ 标假期」：点日历格子勾选，金黄色标记 |
| v1.1.54 | 入场时长分级：首次 3.54s，之后 2.5s |
| v1.1.51 | 卡片与顶栏玻璃化，三维城市背景真正可见 |
| v1.1.50 | 页面背景换成程序生成的等距城市 |
| v1.1.47 | 启动页换成 1080P 视频（去水印、放大锐化） |
| v1.1.45 | 应用图标与启动页徽标统一 |

完整变更记录见交付说明 `WorkTime-定位修复交付说明.md`（本地工作区）。
