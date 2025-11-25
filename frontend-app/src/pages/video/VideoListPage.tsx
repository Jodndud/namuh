import { useEffect, useState } from 'react'
import FootNavbar from '../../components/footernavbar/FootNavbar'
import VideoDetailModal from '../../components/video/VideoDetailModal'
import BackButton from '../../components/Common/BackButton'
import api from '../../lib/api'

const CDN_BASE_URL = (import.meta.env.VITE_CDN_BASE_URL as string) || 'https://media.buriburi.monster/'

const buildCdnUrl = (s3keyOrUrl: string): string => {
  try {
    if (!s3keyOrUrl) return ''
    let key = s3keyOrUrl
    if (/^https?:\/\//i.test(s3keyOrUrl)) {
      const u = new URL(s3keyOrUrl)
      key = u.pathname.replace(/^\/+/, '')
    } else {
      key = s3keyOrUrl.replace(/^\/+/, '')
    }
    const base = CDN_BASE_URL.replace(/\/+$/, '')
    return `${base}/${key}`
  } catch {
    return s3keyOrUrl
  }
}

export default function VideoListPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedSeqNo, setSelectedSeqNo] = useState<number | null>(null)
  const [videos, setVideos] = useState<SmileVideo[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const handleVideoDetailClick = (seqNo: number) => {
    setSelectedSeqNo(seqNo)
    setIsModalOpen(true)
  }

  type SmileVideo = {
    id: number
    owner_id: number
    s3key_or_url: string
    mime_type: string
    type: string
    seq_no: number
    created_at: string
    updated_at: string
  }

  useEffect(() => {
    const fetchSmileVideos = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const res = await api.get('/media/smile-videos')
        const status = res.status
        if (status < 200 || status >= 300) {
          throw new Error(`HTTP ${status}`)
        }
        const data = res.data
        if (!data?.isSuccess) {
          throw new Error(data?.message ?? '요청에 실패했습니다.')
        }
        const result: SmileVideo[] = data?.result ?? []
        setVideos(result)
      } catch (err) {
        const message = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.'
        setError(message)
      } finally {
        setIsLoading(false)
      }
    }
    fetchSmileVideos()
  }, [])

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString)
      if (isNaN(d.getTime())) return ''
      return d.toLocaleDateString('ko-KR')
    } catch {
      return ''
    }
  }

  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold select-none">영상 목록</h1>
      </header>
      <main className="grid grid-cols-2 grid-rows-4 gap-3 px-3 pb-3 select-none">
        {isLoading && (
          <div className="col-span-2 text-center py-8 text-gray-500">로딩 중...</div>
        )}
        {!isLoading && error && (
          <div className="col-span-2 text-center py-8 text-red-500">{error}</div>
        )}
        {!isLoading && !error && videos.length === 0 && (
          <div className="col-span-2 text-center py-8 text-gray-600">표시할 영상이 없습니다.</div>
        )}
        {!isLoading && !error && videos.map((v) => (
          <button key={v.id} onClick={() => handleVideoDetailClick(v.seq_no)}
          className="flex flex-col gap-2 bg-white hover:bg-gray-200 rounded-2xl p-4 w-full h-full
          select-none cursor-pointer active:bg-gray-200 theme-card select-none
          border border-gray-200">
            <p className="text-sm text-left">{formatDate(v.created_at)}</p>
            <div className="rounded-xl overflow-hidden bg-gray-100">
              <img
                src={buildCdnUrl(v.s3key_or_url)}
                alt="영상 썸네일"
                className="w-full h-32 object-cover"
                loading="lazy"
              />
            </div>
          </button>
        ))}
      </main>
      {isModalOpen && selectedSeqNo !== null && (
        <VideoDetailModal seqNo={selectedSeqNo} onClose={() => setIsModalOpen(false)} />
      )}
      <FootNavbar />
    </div>
  )
}

