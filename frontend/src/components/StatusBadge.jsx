export default function StatusBadge({ status }) {
  const s = (status || 'Unknown').toLowerCase()
  const cls = {
    low: 'badge badge-low',
    high: 'badge badge-high',
    normal: 'badge badge-normal',
    unknown: 'badge badge-unknown',
  }[s] || 'badge badge-unknown'

  return <span className={cls}>{status || 'Unknown'}</span>
}
