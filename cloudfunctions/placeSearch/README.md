# 云函数：placeSearch（百度 Place 检索服务端代理）

> 归属任务：任务书 **T6.2**（AK 收敛 + Place API 云函数代理）
> 作用：把「服务端类型 AK」从 APK 客户端移出，只保存在云函数环境变量中，避免随包分发被盗刷。

## 部署步骤（微信云开发 / CloudBase）

1. 在微信开发者工具中打开云开发控制台，新建云函数目录 `placeSearch`（或直接上传本目录）。
2. 在云函数环境变量里配置：
   - `BAIDU_PLACE_AK` = 你的百度「服务端」类型 AK（控制台 → 应用 → 服务端，勾选 Place API/输入提示）
3. 上传并部署（Node.js 运行时；`wx-server-sdk` 已在 package.json 声明）。
4. 验证：云开发控制台 → 云函数 → 测试，传入 `{"query":"苏州火车站","region":"全国"}`，应返回 `{status:0,result:[...]}`。

## 客户端行为（已实现）

`index.html` 的 `searchPlaceSuggestions(query)`：
1. 先调用 `window.CloudSync.cloudCall("placeSearch", {query, region})`；
2. 若云函数未部署/失败，才回退直连百度 Place API（仅当客户端仍配置了 AK；建议后续删除 `BAIDU_PLACE_AK` 注入，让直连路径自然失效）。

## 后续（建议）

- 在 CI `.github/workflows/build-apk.yml` 里删除 `BAIDU_PLACE_AK` secret 注入（改为不再写入 index.html），彻底实现"客户端无服务端 AK"。
- 云函数可加简单频控（同 openid/IP 每分钟 N 次），防止被刷。
- 客户端已做输入防抖；云函数返回仅保留 name/address/location 三个字段。
