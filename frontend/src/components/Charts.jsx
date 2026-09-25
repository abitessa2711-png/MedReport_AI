import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Cell,
} from 'recharts'

const STATUS_COLOR = {
  Low: '#2A5C99',
  High: '#A5342A',
  Normal: '#2C7A4B',
  Unknown: '#8A9A9D',
}

/**
 * Simple bar chart of numeric test results. Each bar is labeled with the
 * test name; unit + reference range are shown in the tooltip so the chart
 * never loses that context.
 */
export default function ResultsChart({ rows }) {
  const data = (rows || [])
    .filter((r) => r.numeric_value !== null && r.numeric_value !== undefined)
    .map((r) => ({
      name: r.test_name.length > 14 ? r.test_name.slice(0, 13) + '…' : r.test_name,
      fullName: r.test_name,
      value: r.numeric_value,
      unit: r.unit,
      range: r.reference_range,
      status: r.status,
    }))

  if (data.length === 0) {
    return <p className="empty-state">No numeric values available to chart.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 42)}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 30 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E4E8E6" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value, _name, item) => [
            `${value} ${item.payload.unit || ''}`.trim(),
            `Reference: ${item.payload.range || 'not provided'}`,
          ]}
          labelFormatter={(_, item) => item?.[0]?.payload?.fullName}
        />
        <Bar dataKey="value" radius={[0, 3, 3, 0]}>
          {data.map((entry, idx) => (
            <Cell key={idx} fill={STATUS_COLOR[entry.status] || STATUS_COLOR.Unknown} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
