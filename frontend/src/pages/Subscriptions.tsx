import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { CreditCard, Check, Zap, XCircle, Receipt } from 'lucide-react'
import { api } from '../lib/api'
import { useToast } from '../context/ToastContext'

interface Plan {
  id: number
  plan_type: string
  name: string
  description?: string
  daily_outfit_limit?: number
  unlimited_recommendations: boolean
  price_monthly: number
  is_active: boolean
}

interface Subscription {
  id: number
  status: string
  plan: Plan
  daily_outfit_count: number
  last_reset_date: string
}

interface Transaction {
  id: number
  amount: number
  currency: string
  status: string
  receipt_url?: string
  created_at: string
}

export default function Subscriptions() {
  const { success, error: showError } = useToast()
  const [plans, setPlans] = useState<Plan[]>([])
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [plansData, subData, txData] = await Promise.all([
        api.get<Plan[]>('/subscriptions/plans'),
        api.get<Subscription>('/subscriptions/me').catch(() => null),
        api.get<Transaction[]>('/subscriptions/transactions').catch(() => []),
      ])
      setPlans(plansData)
      setSubscription(subData)
      setTransactions(Array.isArray(txData) ? txData : [])
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to load')
      setPlans([])
      setSubscription(null)
      setTransactions([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleCheckout = async (planId: number) => {
    try {
      const successUrl = encodeURIComponent(`${window.location.origin}/dashboard`)
      const cancelUrl = encodeURIComponent(`${window.location.origin}/subscriptions`)
      const data = await api.post<{ url?: string }>(
        `/subscriptions/checkout?plan_id=${planId}&success_url=${successUrl}&cancel_url=${cancelUrl}`
      )
      if (data?.url) window.location.href = data.url
      else showError('Checkout URL not available. Stripe may not be configured.')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Checkout failed')
    }
  }

  const handleCancel = async () => {
    if (!confirm('Cancel your subscription? You will keep access until the end of the billing period.')) return
    setCancelling(true)
    try {
      await api.post('/subscriptions/cancel')
      await fetchData()
      success('Subscription will be cancelled at the end of the billing period')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to cancel')
    } finally {
      setCancelling(false)
    }
  }

  return (
    <div>
      <div>
        <h1 className="font-display text-3xl font-bold text-ink-900">Subscriptions</h1>
        <p className="mt-2 text-ink-600">Manage your plan</p>
      </div>

      {loading ? (
        <div className="mt-12 grid gap-6 md:grid-cols-2 max-w-4xl">
          {[1, 2].map((i) => (
            <div key={i} className="card h-64 animate-pulse bg-ink-100" />
          ))}
        </div>
      ) : (
        <div className="mt-10 grid gap-6 md:grid-cols-2 max-w-4xl">
          {plans.map((plan, i) => {
            const isCurrent = subscription?.plan?.id === plan.id
            const isPremium = plan.plan_type?.toLowerCase() === 'premium'
            return (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`card p-8 relative overflow-hidden ${
                  isPremium ? 'ring-2 ring-copper-500' : ''
                }`}
              >
                {isPremium && (
                  <div className="absolute top-4 right-4 px-2 py-1 rounded bg-copper-100 text-copper-700 text-xs font-medium flex items-center gap-1">
                    <Zap size={12} />
                    Popular
                  </div>
                )}
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className={`p-2 rounded-lg ${
                      isPremium ? 'bg-copper-100 text-copper-600' : 'bg-ink-100 text-ink-600'
                    }`}
                  >
                    <CreditCard size={24} />
                  </div>
                  <h3 className="text-xl font-semibold text-ink-900">{plan.name}</h3>
                </div>
                {plan.description && (
                  <p className="text-ink-600 mb-6">{plan.description}</p>
                )}
                <div className="mb-6">
                  <span className="text-3xl font-bold text-ink-900">${plan.price_monthly}</span>
                  <span className="text-ink-500">/month</span>
                </div>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center gap-2 text-ink-700">
                    <Check size={18} className="text-green-600 shrink-0" />
                    {plan.unlimited_recommendations
                      ? 'Unlimited AI recommendations'
                      : `${plan.daily_outfit_limit || 5} recommendations per day`}
                  </li>
                </ul>
                {isCurrent ? (
                  <div className="space-y-2">
                    <div className="px-4 py-2 rounded-lg bg-green-100 text-green-700 text-center font-medium">
                      Current plan
                    </div>
                    {subscription?.status === 'active' && (
                      <button
                        onClick={handleCancel}
                        disabled={cancelling}
                        className="w-full py-2 text-sm text-ink-500 hover:text-red-600"
                      >
                        {cancelling ? 'Cancelling...' : 'Cancel subscription'}
                      </button>
                    )}
                  </div>
                ) : (
                  <button
                    onClick={() => handleCheckout(plan.id)}
                    className={isPremium ? 'btn-accent w-full' : 'btn-secondary w-full'}
                  >
                    Upgrade
                  </button>
                )}
              </motion.div>
            )
          })}
        </div>
      )}

      {(subscription || !loading) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-10 space-y-6"
        >
          {subscription ? (
            <div className="card p-6 max-w-xl">
              <h3 className="font-semibold text-ink-900 mb-4">Current usage</h3>
              <div className="flex items-center gap-4">
                <div>
                  <p className="text-2xl font-bold text-ink-900">
                    {subscription.daily_outfit_count}
                    {subscription.plan?.daily_outfit_limit != null ? (
                      <span className="text-ink-500 font-normal"> / {subscription.plan.daily_outfit_limit}</span>
                    ) : (
                      <span className="text-ink-500 font-normal text-lg"> today</span>
                    )}
                  </p>
                  <p className="text-sm text-ink-500">Recommendations used today</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="card p-6 max-w-xl bg-ink-50">
              <p className="text-ink-600">
                You have a Basic plan (included on registration). Upgrade to Premium for unlimited recommendations.
              </p>
            </div>
          )}

          {transactions.length > 0 && (
            <div className="card p-6 max-w-2xl">
              <h3 className="font-semibold text-ink-900 mb-4 flex items-center gap-2">
                <Receipt size={20} />
                Payment history
              </h3>
              <div className="space-y-3">
                {transactions.slice(0, 10).map((tx) => (
                  <div
                    key={tx.id}
                    className="flex items-center justify-between py-2 border-b border-ink-100 last:border-0"
                  >
                    <div>
                      <span className="font-medium">${tx.amount} {tx.currency}</span>
                      <span
                        className={`ml-2 text-xs px-2 py-0.5 rounded ${
                          tx.status === 'completed'
                            ? 'bg-green-100 text-green-700'
                            : tx.status === 'failed'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-ink-100 text-ink-600'
                        }`}
                      >
                        {tx.status}
                      </span>
                    </div>
                    <span className="text-sm text-ink-500">
                      {new Date(tx.created_at).toLocaleDateString()}
                    </span>
                    {tx.receipt_url && (
                      <a
                        href={tx.receipt_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-copper-600 hover:underline"
                      >
                        Receipt
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}
