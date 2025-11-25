async function DownloadVideo(src: string) {
  try {
    const response = await fetch(src);
    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = `video_${Date.now()}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(blobUrl);
  } catch {
    alert("다운로드에 실패했습니다.");
  }
}

export default function DownloadButton({ src }: { src: string }) {
  return (
    <button
      className="flex items-center gap-2 justify-center bg-gray-200 p-4 rounded-2xl border
    active:bg-lime-500 active:text-white select-none cursor-pointer theme-button select-none"
      onClick={() => DownloadVideo(src)}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-6 h-6"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
      다운로드
    </button>
  );
}
