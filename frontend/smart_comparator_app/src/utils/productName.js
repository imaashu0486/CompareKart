function toText(value) {
  return String(value || '').trim().replace(/\s+/g, ' ');
}

export function getPrimaryProductName(item) {
  const brand = toText(item?.brand);
  const model = toText(item?.model);
  const variant = toText(item?.variant_name);

  const baseName = `${brand} ${model}`.trim();
  if (baseName) return baseName;
  if (variant) return variant;
  return 'Phone';
}

export function getVariantBadgeText(item) {
  const brand = toText(item?.brand).toLowerCase();
  const model = toText(item?.model).toLowerCase();
  const variant = toText(item?.variant_name);
  if (!variant) return null;

  const variantLc = variant.toLowerCase();
  const includesBase = (brand && variantLc.includes(brand)) || (model && variantLc.includes(model));
  return includesBase ? null : variant;
}
