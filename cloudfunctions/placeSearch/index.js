// T6.2：百度 Place Web API 服务端代理云函数（微信云开发 / CloudBase 均可部署）
// 目的：把「服务端类型 AK」从 APK 客户端移出，改为只存在云函数环境变量 BAIDU_PLACE_AK 里。
// 客户端调用：window.CloudSync.cloudCall("placeSearch", { query, region })
// 返回：{ status: 0, result: [{ name, address, location: { lat, lng } }] }
//      status 非 0 时 result 缺失，message 说明原因。
const cloud = require("wx-server-sdk");
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const https = require("https");

function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, (res) => {
      let body = "";
      res.setEncoding("utf8");
      res.on("data", (chunk) => { body += chunk; });
      res.on("end", () => {
        try { resolve(JSON.parse(body)); } catch (e) { reject(e); }
      });
    });
    req.on("error", reject);
    req.setTimeout(6000, () => { req.destroy(new Error("upstream timeout")); });
  });
}

exports.main = async (event) => {
  const query = String((event && event.query) || "").trim();
  const region = String((event && event.region) || "全国").trim();
  if (!query || query.length > 40) return { status: 1, message: "query invalid" };
  const ak = process.env.BAIDU_PLACE_AK;
  if (!ak) return { status: 2, message: "server AK not configured (env BAIDU_PLACE_AK)" };

  const url = "https://api.map.baidu.com/place/v2/suggestion?query=" + encodeURIComponent(query) +
    "&region=" + encodeURIComponent(region) + "&output=json&ak=" + encodeURIComponent(ak);
  let data;
  try {
    data = await httpGetJson(url);
  } catch (e) {
    return { status: 3, message: "upstream error: " + (e && e.message ? e.message : e) };
  }
  if (!data || data.status !== 0 || !Array.isArray(data.result)) {
    return { status: (data && data.status) || 9, message: (data && data.message) || "upstream error" };
  }
  // 只回传客户端需要的字段，减小响应 + 降低数据面
  return {
    status: 0,
    result: data.result.slice(0, 10).map((it) => ({
      name: it.name,
      address: it.address,
      location: it.location
    }))
  };
};
