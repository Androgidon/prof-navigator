export function DirtyIndicator({ dirty }: { dirty: boolean }) {
  if (!dirty) {
    return null;
  }
  return <span className="admin-dirty-indicator">● Несохраненные изменения</span>;
}
