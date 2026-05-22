/**
 * useBreakpoint — detecta el breakpoint Tailwind activo.
 *
 * Uso:
 *   const { isMobile, isTablet, isDesktop, breakpoint } = useBreakpoint()
 *
 * isMobile  → < 640px  (sm)
 * isTablet  → 640-1023px (sm a lg)
 * isDesktop → >= 1024px (lg+)
 * breakpoint → 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
 */
import { ref, onMounted, onUnmounted } from 'vue'

const BREAKPOINTS = { sm: 640, md: 768, lg: 1024, xl: 1280, '2xl': 1536 }

function getCurrentBreakpoint(w) {
  if (w >= 1536) return '2xl'
  if (w >= 1280) return 'xl'
  if (w >= 1024) return 'lg'
  if (w >= 768)  return 'md'
  if (w >= 640)  return 'sm'
  return 'xs'
}

export function useBreakpoint() {
  const breakpoint = ref(getCurrentBreakpoint(window.innerWidth))
  const width      = ref(window.innerWidth)

  function onResize() {
    width.value = window.innerWidth
    breakpoint.value = getCurrentBreakpoint(width.value)
  }

  onMounted(() => window.addEventListener('resize', onResize))
  onUnmounted(() => window.removeEventListener('resize', onResize))

  return {
    breakpoint,
    width,
    isMobile:  () => width.value < 640,
    isTablet:  () => width.value >= 640 && width.value < 1024,
    isDesktop: () => width.value >= 1024,
    atLeast:   (bp) => width.value >= (BREAKPOINTS[bp] ?? 0),
  }
}
