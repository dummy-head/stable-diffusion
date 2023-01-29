import { d as defineComponent, q as createBlock, e as unref, o as openBlock, R as NProgress } from "./index.js";
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "StatsView",
  setup(__props) {
    return (_ctx, _cache) => {
      return openBlock(), createBlock(unref(NProgress), {
        type: "dashboard",
        percentage: 80
      });
    };
  }
});
export {
  _sfc_main as default
};
