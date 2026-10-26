// rows: any[] - The data to be exported as CSV.
// filename: string - The base name for the exported CSV file.
export function tableToCsv(rows: any, filename: string): void {
    // If there are no rows to export, log a warning and return early.
    if (!rows.length) {
        console.warn('No data to export.');
        return;
    }

    // Converts the rows to CSV format and create a downloadable link.
    const csv = toCsv(rows);
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}-${stamp}.csv`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Helper Functions
// Flattens a nested object into a single-level object with dot-notation keys
function flatten(obj: any, prefix = '', out: Record<string, any> = {}): Record<string, any> {
    for (const [key, value] of Object.entries(obj)) {
        const k = prefix ? `${prefix}.${key}` : key;
    
        const isPlainObject = value !== null &&
        typeof value === 'object' &&
        !Array.isArray(value) &&
        !(value instanceof Date) &&
        Object.keys(value as object).length > 0;

        if (isPlainObject) {
            flatten(value, k, out);
        } else {
            out[k] = value;
        }
    }
    return out;
}

// RFC 4180 cell escaping
function cell(value: any): string {
    if (value === null || value === undefined) {
        return '';
    }
    let s = typeof value === 'object' ? JSON.stringify(value) : String(value);
    if (/[",\r\n]/.test(s)) {
        s = '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
}

// Converts to the CSV
function toCsv(rows: any[]): string {
    const flat = rows.map(r => flatten(r));

    // Union of all keys, preserving first-seen order
    const headers: string[] = [];
    const seen = new Set<string>();
    for (const row of flat) {
        for (const k of Object.keys(row)) {
            if (!seen.has(k)) { 
                seen.add(k); headers.push(k);
            }
        }
    }
    // Create CSV lines
    const lines = [headers.map(h => cell(h)).join(',')];
    for (const row of flat) {
        lines.push(headers.map(h => cell(row[h])).join(','));
    }
    return lines.join('\r\n') + '\r\n';
}