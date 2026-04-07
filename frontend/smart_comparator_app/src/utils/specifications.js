const toText = (value) => {
  if (value === null || value === undefined) return null;
  const str = String(value).trim();
  return str.length ? str : null;
};

const normalizeMap = (specs) => {
  const out = {};
  Object.entries(specs || {}).forEach(([k, v]) => {
    const key = String(k || '').trim().toLowerCase();
    const val = toText(v);
    if (!key || !val) return;
    out[key] = val;
  });
  return out;
};

const findSpec = (map, candidates = [], contains = []) => {
  for (const key of candidates) {
    if (map[key]) return map[key];
  }
  for (const [k, v] of Object.entries(map)) {
    if (contains.some((token) => k.includes(token))) {
      return v;
    }
  }
  return null;
};

const findRegex = (text, pattern) => {
  if (!text) return null;
  const m = String(text).match(pattern);
  return m ? m[0].replace(/\s+/g, ' ').trim() : null;
};

export function getFixedPhoneSpecificationRows(item) {
  const specs = normalizeMap(item?.specifications || {});
  const variant = toText(item?.variant_name) || '';

  const display =
    findSpec(specs, ['display', 'display type', 'screen size']) ||
    findSpec(specs, [], ['display', 'screen']);

  const processor =
    findSpec(specs, ['chipset', 'processor', 'processor speed', 'cpu speed']) ||
    findSpec(specs, [], ['chipset', 'processor', 'cpu']);

  const ram =
    findSpec(specs, ['ram', 'ram memory installed size', 'ram memory installed']) ||
    findRegex(variant, /\b\d{1,2}\s*gb\s*ram\b/i) ||
    findSpec(specs, [], ['ram']);

  const storage =
    findSpec(specs, ['storage', 'memory storage capacity', 'internal storage']) ||
    findRegex(variant, /\b\d{2,4}\s*(gb|tb)\b/i) ||
    findSpec(specs, [], ['storage', 'rom']);

  const rearCamera =
    findSpec(specs, ['rear camera', 'primary camera', 'camera']) ||
    findSpec(specs, [], ['rear camera', 'primary camera', 'camera']);

  const frontCamera =
    findSpec(specs, ['front camera', 'selfie camera']) ||
    findSpec(specs, [], ['front camera', 'selfie']);

  const battery =
    findSpec(specs, ['battery', 'battery power']) ||
    findRegex(variant, /\b\d{3,5}\s*mah\b/i) ||
    findSpec(specs, [], ['battery']);

  const operatingSystem =
    findSpec(specs, ['operating system', 'os']) ||
    findSpec(specs, [], ['operating system', ' os']);

  const network =
    findSpec(specs, ['cellular technology', 'network connectivity technology', 'wireless provider']) ||
    findSpec(specs, [], ['cellular', 'network', '5g', '4g']);

  const color = findSpec(specs, ['colour', 'color']);

  const rows = [
    { key: 'brand', label: 'Brand', value: toText(item?.brand) },
    { key: 'model', label: 'Model', value: toText(item?.model) },
    { key: 'variant', label: 'Variant', value: toText(item?.variant_name) },
    { key: 'display', label: 'Display', value: display },
    { key: 'processor', label: 'Processor', value: processor },
    { key: 'ram', label: 'RAM', value: ram },
    { key: 'storage', label: 'Storage', value: storage },
    { key: 'rear_camera', label: 'Rear Camera', value: rearCamera },
    { key: 'front_camera', label: 'Front Camera', value: frontCamera },
    { key: 'battery', label: 'Battery', value: battery },
    { key: 'os', label: 'Operating System', value: operatingSystem },
    { key: 'network', label: 'Network', value: network },
    { key: 'color', label: 'Color', value: color },
  ];

  return rows.map((row) => ({ ...row, value: row.value || 'Not available' }));
}
