import { useRef } from 'react'

export type SegmentAudioPlayerProps = {
  src?: string
  onTimeUpdate?: (currentTime: number) => void
}

export function SegmentAudioPlayer({ src, onTimeUpdate }: SegmentAudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)

  return (
    <audio
      ref={audioRef}
      controls
      src={src}
      onTimeUpdate={() => {
        if (audioRef.current && onTimeUpdate) {
          onTimeUpdate(audioRef.current.currentTime)
        }
      }}
    />
  )
}

export function getCurrentPlaybackSeconds(
  player: HTMLAudioElement | null,
): number {
  return player?.currentTime ?? 0
}
