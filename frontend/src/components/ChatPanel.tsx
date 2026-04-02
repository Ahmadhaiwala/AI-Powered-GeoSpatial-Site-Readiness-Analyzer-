import { useState, useRef, useEffect } from 'react'
import { MessageCircle, Send, X, Loader2, ThumbsUp } from 'lucide-react'
import { useMapStore } from '../store'
import { api } from '../lib/api'

export function ChatPanel() {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  const {
    chatMessages,
    addChatMessage,
    showChat,
    toggleChat,
    isChatLoading,
    setChatLoading,
    businessType,
    selectedLocation,
  } = useMapStore()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || isChatLoading) return
    setInput('')

    addChatMessage({ role: 'user', content: text })
    setChatLoading(true)

    try {
      const res = await api.chat(text)
      addChatMessage({
        role: 'assistant',
        content: res.reply,
        results: res.results,
      })
    } catch (err) {
      addChatMessage({
        role: 'assistant',
        content: '⚠️ Could not reach the backend. Make sure the server is running.',
      })
    } finally {
      setChatLoading(false)
    }
  }

  const castVote = async () => {
    if (!selectedLocation) {
      addChatMessage({
        role: 'assistant',
        content: '📍 Click on the map first to select a location before voting.',
      })
      return
    }
    try {
      const res = await api.vote(selectedLocation.lat, selectedLocation.lng, businessType)
      addChatMessage({ role: 'assistant', content: `🗳️ ${res.message}` })
    } catch {
      addChatMessage({ role: 'assistant', content: '⚠️ Vote failed. Backend may be offline.' })
    }
  }

  if (!showChat) return null

  return (
    <div
      onClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.stopPropagation()}
      onPointerDown={(e) => e.stopPropagation()}
      style={{ zIndex: 1000, pointerEvents: 'auto' }}
      className="absolute bottom-4 left-1/2 -translate-x-1/2 w-[420px] rounded-xl shadow-2xl flex flex-col max-h-[480px] overflow-hidden border border-white/10"
    >
      {/* Header */}
      <div
        className="p-3 border-b border-white/10 flex items-center justify-between"
        style={{ background: 'rgba(15,23,42,0.92)', backdropFilter: 'blur(12px)' }}
      >
        <div className="flex items-center gap-2">
          <MessageCircle size={18} className="text-emerald-400" />
          <span className="font-semibold text-white text-sm">AI Location Assistant</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={castVote}
            title="Vote demand for this location"
            className="flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-700 hover:bg-emerald-700 text-slate-300 hover:text-white text-xs transition-all"
          >
            <ThumbsUp size={13} />
            Vote Here
          </button>
          <button onClick={toggleChat} className="p-1 rounded hover:bg-slate-700 text-slate-400">
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div
        className="flex-1 overflow-y-auto p-3 space-y-2 min-h-0"
        style={{ background: 'rgba(15,23,42,0.88)', backdropFilter: 'blur(12px)' }}
      >
        {chatMessages.length === 0 && (
          <p className="text-xs text-slate-400 text-center py-4">
            Ask me: "Find best salon near Vastrapur" or "Where should I open a warehouse?"
          </p>
        )}
        {chatMessages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] px-3 py-2 rounded-xl text-xs leading-relaxed whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-emerald-700 text-white rounded-br-sm'
                  : 'bg-slate-700 text-slate-200 rounded-bl-sm'
              }`}
            >
              {msg.content}
              {msg.results && msg.results.length > 0 && (
                <div className="mt-2 space-y-1">
                  {msg.results.slice(0, 5).map((r) => (
                    <div
                      key={r.h3_index}
                      className="flex justify-between items-center px-2 py-1 bg-slate-800/50 rounded text-xs"
                    >
                      <span className="text-slate-300">
                        #{r.rank} — {r.lat.toFixed(4)}, {r.lng.toFixed(4)}
                      </span>
                      <span className="font-bold text-emerald-400">{r.score}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isChatLoading && (
          <div className="flex justify-start">
            <div className="px-3 py-2 bg-slate-700 rounded-xl rounded-bl-sm flex items-center gap-2">
              <Loader2 size={12} className="animate-spin text-emerald-400" />
              <span className="text-xs text-slate-400">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div
        className="p-3 border-t border-white/10 flex gap-2"
        style={{ background: 'rgba(15,23,42,0.92)', backdropFilter: 'blur(12px)' }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about locations…"
          className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500"
        />
        <button
          onClick={sendMessage}
          disabled={isChatLoading || !input.trim()}
          className="p-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-white transition-colors"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
