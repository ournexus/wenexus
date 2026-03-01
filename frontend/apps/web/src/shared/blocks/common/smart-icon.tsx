import { ComponentType, lazy, Suspense } from 'react';

const iconCache: { [key: string]: ComponentType<any> } = {};

export function SmartIcon({
  name,
  size = 24,
  className,
  ...props
}: {
  name: string;
  size?: number;
  className?: string;
  [key: string]: any;
}) {
  if (!iconCache[name]) {
    iconCache[name] = lazy(async () => {
      try {
        const module = await import('lucide-react');
        const IconComponent = module[name as keyof typeof module];
        if (IconComponent) {
          return { default: IconComponent as ComponentType<any> };
        }
        return { default: module.HelpCircle as ComponentType<any> };
      } catch {
        const fallback = await import('lucide-react');
        return { default: fallback.HelpCircle as ComponentType<any> };
      }
    });
  }

  const IconComponent = iconCache[name];

  return (
    <Suspense fallback={<div style={{ width: size, height: size }} />}>
      <IconComponent size={size} className={className} {...props} />
    </Suspense>
  );
}
