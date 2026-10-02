/** Pure, explicitly synthetic example; replace with the application's repository. */
export function inspectEntity(id) {
  if (typeof id !== 'string' || id.trim() === '') throw new TypeError('id must be non-empty');
  return id === 'example:equipment-1'
    ? { status: 'example', id, label: 'Example equipment', entityType: 'Equipment' }
    : { status: 'not-found', id, label: '', entityType: '' };
}
