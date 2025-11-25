function RecordingStatus() {
  const bars = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

  return (
    <div className="p-3 bg-black/40 border border-red-500/20 rounded hover:border-red-500/40 transition-all">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-sm text-gray-400">Recording</span>
        </div>
        <span className="text-md font-bold text-red-400">Active</span>
      </div>

      {/* 웨이브폼 영역 */}
      <div className="relative h-8 bg-black/60 rounded flex items-center justify-around px-1 gap-0.5">
        {bars.map((i) => (
          <div
            key={i}
            className="w-1 bg-red-400 rounded-full"
            style={{
              animation: `waveBar 0.8s ease-in-out infinite`,
              animationDelay: `${i * 0.05}s`,
              boxShadow: "0 0 4px rgba(248, 113, 113, 0.6)",
            }}
          />
        ))}
      </div>

      <div className="text-sm text-gray-500 mt-1 pl-1">2h 34m</div>

      {/* 웨이브폼 애니메이션 CSS */}
      <style>{`
        @keyframes waveBar {
          0%, 100% { height: 8px; opacity: 0.4; }
          50% { height: 16px; opacity: 1; }
        }
      `}</style>
    </div>
  );
}

// AI 모델 상태
function AIModelStatus() {
  return (
    <div className="p-3 bg-black/40 border border-blue-500/20 rounded hover:border-blue-500/40 transition-all">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500" />
          <span className="text-sm text-gray-400">AI Model</span>
        </div>
        <span className="text-md font-bold text-blue-400">Running</span>
      </div>
      <div className="text-sm text-gray-500">
        <div>Model: v2.1.0</div>
        <div>Inference: 12ms avg</div>
      </div>
    </div>
  );
}

// 연결 상태
function ConnectionStatus() {
  return (
    <div className="p-3 bg-black/40 border border-green-500/20 rounded hover:border-green-500/40 transition-all">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-sm text-gray-400">Connection</span>
        </div>
        <span className="text-md font-bold text-green-400">Stable</span>
      </div>
      <div className="text-sm text-gray-500">
        <div>Latency: 24ms</div>
        <div>Signal: 94.4%</div>
      </div>
    </div>
  );
}

export default function SystemStatus() {
  return (
    <div className="space-y-3">
      <h2 className="text-md font-semibold text-white mb-4">SYSTEM STATUS</h2>
      <RecordingStatus />
      <AIModelStatus />
      <ConnectionStatus />
    </div>
  );
}
