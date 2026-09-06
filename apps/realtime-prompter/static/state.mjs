export function initialState() {
  return { revision: 0, confirmed: "", partial: "", answer: "", status: "待機", ttft: null, final: false };
}

export function reduce(state, event) {
  if (event.type === "reset") return { ...initialState(), revision: event.revision };
  if (event.type === "transcript") {
    if (event.revision <= state.revision) return state;
    return { ...state, revision: event.revision, confirmed: event.confirmed, partial: event.partial,
      answer: "", status: "生成待ち", ttft: null, final: event.is_final };
  }
  if (event.revision !== state.revision) return state;
  switch (event.type) {
    case "generation_start": return { ...state, answer: "", status: "生成中" };
    case "generation_delta": return { ...state, answer: state.answer + event.text, ttft: event.ttft_ms ?? state.ttft };
    case "generation_done": return { ...state, status: "完了" };
    case "error": return { ...state, status: "生成エラー" };
    default: return state;
  }
}
