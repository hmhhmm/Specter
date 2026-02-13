export function RevenueEpicenter() {
  return (
    <div className="rounded-2xl border-2 border-white/10 bg-gradient-to-br from-zinc-900/80 to-zinc-900/40 backdrop-blur-sm p-6 h-full">
      <h3 className="text-lg font-bold mb-6">Revenue Impact</h3>
      
      <div className="relative mb-8">
        <div className="flex items-baseline gap-3 mb-2">
          <span className="text-5xl font-bold bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">$12.4K</span>
          <div className="flex flex-col">
            <span className="text-xs text-zinc-500 uppercase">Estimated Daily Loss</span>
            <span className="text-sm text-red-400 font-semibold">↓ 18% conversion</span>
          </div>
        </div>
      </div>

      <div className="space-y-5">
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-zinc-300">Checkout Abandonment</span>
            <span className="text-sm font-bold text-red-400">42%</span>
          </div>
          <div className="relative h-2 bg-white/5 rounded-full overflow-hidden">
            <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-red-500 to-red-600 rounded-full" style={{width: '42%'}} />
          </div>
          <p className="text-xs text-zinc-500 mt-1">Chat widget blocking CTA button</p>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-zinc-300">Form Drop-off Rate</span>
            <span className="text-sm font-bold text-orange-400">28%</span>
          </div>
          <div className="relative h-2 bg-white/5 rounded-full overflow-hidden">
            <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full" style={{width: '28%'}} />
          </div>
          <p className="text-xs text-zinc-500 mt-1">Keyboard focus trap in modal</p>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-zinc-300">Mobile Bounce Rate</span>
            <span className="text-sm font-bold text-yellow-400">15%</span>
          </div>
          <div className="relative h-2 bg-white/5 rounded-full overflow-hidden">
            <div className="absolute inset-y-0 left-0 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-full" style={{width: '15%'}} />
          </div>
          <p className="text-xs text-zinc-500 mt-1">Unresponsive UI on slow networks</p>
        </div>
      </div>
    </div>
  );
}
