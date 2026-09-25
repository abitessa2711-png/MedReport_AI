import StatusBadge from './StatusBadge'

/**
 * Editable table of OCR-extracted rows. Lets the user correct a misread
 * value/unit/reference range before the AI summary is generated - this is
 * the "handle OCR errors gracefully" requirement.
 */
export default function ResultsTable({ rows, editable, onChangeRow }) {
  if (!rows || rows.length === 0) {
    return <p className="empty-state">No test rows extracted yet.</p>
  }

  return (
    <table className="results-table">
      <thead>
        <tr>
          <th>Test name</th>
          <th>Value</th>
          <th>Unit</th>
          <th>Reference range</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>
              {editable ? (
                <input
                  value={row.test_name || ''}
                  onChange={(e) => onChangeRow(row.id, 'test_name', e.target.value)}
                />
              ) : (
                row.test_name
              )}
              {row.was_corrected && <span className="corrected-mark">edited</span>}
            </td>
            <td>
              {editable ? (
                <input
                  value={row.value ?? ''}
                  onChange={(e) => onChangeRow(row.id, 'value', e.target.value)}
                />
              ) : (
                row.value ?? '—'
              )}
            </td>
            <td>
              {editable ? (
                <input
                  value={row.unit ?? ''}
                  onChange={(e) => onChangeRow(row.id, 'unit', e.target.value)}
                />
              ) : (
                row.unit ?? '—'
              )}
            </td>
            <td>
              {editable ? (
                <input
                  value={row.reference_range ?? ''}
                  placeholder="not provided"
                  onChange={(e) => onChangeRow(row.id, 'reference_range', e.target.value)}
                />
              ) : (
                row.reference_range ?? 'Not provided'
              )}
            </td>
            <td><StatusBadge status={row.status} /></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
