import EventTimeline from '../monitoring/EventTimeline'
import RobotPOV from '../monitoring/RobotPOV'
import Scene3D from '../3d/Scene3D'

interface RightPanelProps {
  onToggleSwap: () => void
  isRobotInCenter: boolean
}

export default function RightPanel({ onToggleSwap, isRobotInCenter }: RightPanelProps) {
  return (
    <div className="col-span-1 w-full h-screen bg-black/40 backdrop-blur-md z-10 flex flex-col">
      <div className="h-full py-4 pr-4 flex flex-col overflow-y-auto">
        {/* Robot POV */}
        <div className="mb-4">
          <div
            className="h-[30vh] cursor-pointer"
            onDoubleClick={onToggleSwap}
            title="더블클릭하여 중앙 화면과 교체"
          >
            {isRobotInCenter ? (
              <RobotPOV />
            ) : (
              <div className="w-full h-full bg-black border border-cyan-500/30 rounded overflow-hidden">
                <Scene3D />
              </div>
            )}
          </div>
        </div>

        {/* Event Timeline */}
        <div className="flex-1 min-h-0">
          <EventTimeline />
        </div>

        {/* AI Inference Results */}
        {/* <h2 className="text-lg font-semibold text-cyan-400 mb-4">
          AI Inference
        </h2>
        <div className="mb-8">
          <AIInference />
        </div> */}

        {/* Smile Detection Events */}
        {/* <h2 className="text-lg font-semibold text-cyan-400 mb-4">
          Smile Detection Events
        </h2>

        <div className="space-y-3 mb-8">
          {smileEvents.map((event, index) => (
            <div
              key={index}
              className="p-3 bg-black/40 border border-cyan-500/20 rounded hover:border-cyan-500/40 transition-all cursor-pointer"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-400 font-mono">{event.time}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  event.status === 'saved'
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {event.status}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-cyan-400">Confidence: {event.confidence}</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Duration: {event.duration}
              </div>
            </div>
          ))}
        </div> */}

        {/* Generated Clips */}
        {/* <h2 className="text-lg font-semibold text-purple-400 mb-4">
          Generated Clips
        </h2>

        <div className="space-y-2 mb-6">
          {clips.map((clip) => (
            <div
              key={clip.id}
              className="p-3 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded hover:border-purple-500/50 transition-all cursor-pointer"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-purple-300 font-medium">
                    Clip #{clip.id}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {clip.time} - {clip.size}
                  </div>
                </div>
                <button className="px-3 py-1 bg-purple-500/30 hover:bg-purple-500/50 border border-purple-500/50 rounded text-xs text-purple-200 transition-all">
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>

        <button className="w-full py-3 px-4 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 border border-cyan-500/50 rounded text-sm text-cyan-300 transition-all">
          View All Clips
        </button> */}
      </div>
    </div>
  )
}
