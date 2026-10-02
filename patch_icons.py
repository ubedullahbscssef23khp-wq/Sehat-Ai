with open('frontend/src/components/Icons.tsx', 'r') as f:
    c = f.read()

if 'ActivityIcon' not in c:
    c += '''
export function ActivityIcon({ size = 16 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  );
}
'''
with open('frontend/src/components/Icons.tsx', 'w') as f:
    f.write(c)
