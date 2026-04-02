import { useMapStore } from '../store'
import { ShoppingCart, Utensils, Coffee, Building2, Zap, Heart, Warehouse, Scissors } from 'lucide-react'

// These keys match the backend BUSINESS_WEIGHTS config exactly
const businessTypes = [
  { id: 'retail_store', label: 'Retail', icon: ShoppingCart },
  { id: 'restaurant', label: 'Restaurant', icon: Utensils },
  { id: 'salon', label: 'Salon', icon: Scissors },
  { id: 'gym', label: 'Gym', icon: Zap },
  { id: 'ev_charging', label: 'EV Charging', icon: Coffee },
  { id: 'hospital', label: 'Hospital', icon: Heart },
  { id: 'warehouse', label: 'Warehouse', icon: Warehouse },
]

export function BusinessTypeSelector() {
  const businessType = useMapStore((state) => state.businessType)
  const setBusinessType = useMapStore((state) => state.setBusinessType)

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-slate-300">Business Type</label>
      <div className="grid grid-cols-2 gap-2">
        {businessTypes.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setBusinessType(id)}
            className={`p-2 rounded-lg flex flex-col items-center gap-1 transition-all ${
              businessType === id
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <Icon size={18} />
            <span className="text-xs font-medium text-center leading-tight">{label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
