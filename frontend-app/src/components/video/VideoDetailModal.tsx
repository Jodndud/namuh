import { useEffect, useState } from "react";
import DownloadButton from "./DownloadButton";
import api from "../../lib/api";

export type VideoDetailModalProps = {
  onClose: () => void;
  seqNo: number;
};

type SmileVideoAsset = {
  id: number;
  owner_id: number;
  s3key_or_url: string;
  mime_type: string;
  type: string;
  seq_no: number;
  created_at: string;
  updated_at: string;
};

const CDN_BASE_URL =
  (import.meta.env.VITE_CDN_BASE_URL as string) ||
  "https://media.buriburi.monster/";
const buildCdnUrl = (s3keyOrUrl: string): string => {
  try {
    if (!s3keyOrUrl) return "";
    let key = s3keyOrUrl;
    if (/^https?:\/\//i.test(s3keyOrUrl)) {
      const u = new URL(s3keyOrUrl);
      key = u.pathname.replace(/^\/+/, "");
    } else {
      key = s3keyOrUrl.replace(/^\/+/, "");
    }
    const base = CDN_BASE_URL.replace(/\/+$/, "");
    return `${base}/${key}`;
  } catch {
    return s3keyOrUrl;
  }
};

function formatDate(isoString?: string) {
  if (!isoString) return "";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return "";
    return d.toLocaleDateString("ko-KR");
  } catch {
    return "";
  }
}

export default function VideoDetailModal({
  onClose,
  seqNo,
}: VideoDetailModalProps) {
  const [items, setItems] = useState<SmileVideoAsset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const res = await api.get(`/media/smile-videos/${seqNo}`);
        const status = res.status;
        if (status < 200 || status >= 300) throw new Error(`HTTP ${status}`);
        const data = res.data;
        if (!data?.isSuccess)
          throw new Error(data?.message ?? "요청에 실패했습니다.");
        const result: SmileVideoAsset[] = data?.result ?? [];
        setItems(result.slice(0, 2));
      } catch (e) {
        setError(
          e instanceof Error ? e.message : "알 수 없는 오류가 발생했습니다."
        );
      } finally {
        setIsLoading(false);
      }
    };
    fetchDetail();
  }, [seqNo]);

  return (
    <div
      className="fixed inset-0 bg-black/80 flex items-center justify-center"
      onClick={onClose}
    >
      <div
        className="flex flex-col gap-4 bg-white rounded-2xl border border-gray-300 p-4 w-[90%] max-w-md theme-card select-none"
        onClick={(e) => e.stopPropagation()}
      >
        <h1 className="text-left text-md font-semibold">
          {formatDate(items[0]?.created_at) || ``}
        </h1>

        {isLoading && (
          <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">
            로딩 중...
          </div>
        )}

        {!isLoading && error && (
          <div className="aspect-video bg-red-50 text-red-600 rounded-lg flex items-center justify-center px-4 text-sm">
            {error}
          </div>
        )}

        {!isLoading && !error && items.length === 0 && (
          <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">
            영상이 없습니다.
          </div>
        )}

        {!isLoading && !error && items.length > 0 && (
          <div className="flex flex-col gap-4">
            {items.map((it) => {
              const src = buildCdnUrl(it.s3key_or_url);
              const isVideo = /^video\//i.test(it.mime_type);
              return (
                <div key={it.id} className="w-full">
                  {isVideo ? (
                    <video
                      src={src}
                      controls
                      playsInline
                      className="w-full rounded-lg bg-black"
                    />
                  ) : (
                    <img
                      src={src}
                      alt="영상 이미지"
                      className="w-full rounded-lg object-contain bg-gray-100"
                    />
                  )}
                </div>
              );
            })}
          </div>
        )}

        <DownloadButton src={buildCdnUrl(items[0]?.s3key_or_url)} />
      </div>
    </div>
  );
}
