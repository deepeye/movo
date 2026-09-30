<script setup lang="ts">
import { computed } from 'vue'

export type DesktopPrimarySection = 'home' | 'scheduled' | 'skills' | 'tools' | 'knowledge'

interface NavigationItem {
  id: DesktopPrimarySection
  zh: string
  en: string
  visible: boolean
  badge: number
}

const props = withDefaults(defineProps<{
  active: DesktopPrimarySection
  locale?: 'zh' | 'en'
  skillsAvailable?: boolean
  toolsAvailable?: boolean
  knowledgeAvailable?: boolean
  skillBadge?: number
  knowledgeBadge?: number
}>(), {
  locale: 'zh',
  skillsAvailable: true,
  toolsAvailable: true,
  knowledgeAvailable: true,
  skillBadge: 0,
  knowledgeBadge: 0,
})

const emit = defineEmits<{ (event: 'navigate', section: DesktopPrimarySection): void }>()

const items = computed<NavigationItem[]>(() => [
  { id: 'home', zh: '首页', en: 'Home', visible: true, badge: 0 },
  { id: 'scheduled', zh: '定时', en: 'Tasks', visible: true, badge: 0 },
  { id: 'skills', zh: 'Skill', en: 'Skills', visible: props.skillsAvailable, badge: props.skillBadge },
  { id: 'tools', zh: 'MCP', en: 'MCP', visible: props.toolsAvailable, badge: 0 },
  { id: 'knowledge', zh: '知识库', en: 'Knowledge Base', visible: props.knowledgeAvailable, badge: props.knowledgeBadge },
])
</script>

<template>
  <nav class="desktop-primary-nav" :aria-label="locale === 'en' ? 'Primary navigation' : '主导航'">
    <div class="desktop-primary-nav__items">
      <button
        v-for="item in items.filter(entry => entry.visible)"
        :key="item.id"
        type="button"
        class="desktop-primary-nav__item"
        :class="{ active: active === item.id }"
        :aria-current="active === item.id ? 'page' : undefined"
        :aria-label="locale === 'en' ? item.en : item.zh"
        :data-tooltip="locale === 'en' ? item.en : item.zh"
        @click="emit('navigate', item.id)"
      >
        <span class="desktop-primary-nav__icon" aria-hidden="true">
          <svg v-if="item.id === 'home'" viewBox="0 0 24 24"><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1V10Z"/></svg>
          <svg v-else-if="item.id === 'scheduled'" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
          <svg v-else-if="item.id === 'skills'" viewBox="0 0 24 24"><path d="m12 3 1.35 3.65L17 8l-3.65 1.35L12 13l-1.35-3.65L7 8l3.65-1.35L12 3Z"/><path d="m5 13 .9 2.1L8 16l-2.1.9L5 19l-.9-2.1L2 16l2.1-.9L5 13Zm14-1 .9 2.1 2.1.9-2.1.9L19 18l-.9-2.1L16 15l2.1-.9L19 12Z"/></svg>
          <svg v-else-if="item.id === 'tools'" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><circle cx="4" cy="7" r="2"/><circle cx="20" cy="7" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="m6 8 3.5 2.5M18 8l-3.5 2.5M7 18l3-3.5m7 3.5-3-3.5"/></svg>
          <svg v-else viewBox="0 0 24 24"><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H20v18H7.5A2.5 2.5 0 0 0 5 22V4.5Z"/><path d="M5 19.5A2.5 2.5 0 0 1 7.5 17H20"/></svg>
        </span>
        <span v-if="item.badge > 0" class="desktop-primary-nav__badge" aria-hidden="true">{{ item.badge > 99 ? '99+' : item.badge }}</span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.desktop-primary-nav {
  --desktop-nav-bg: #f3f6fa;
  --desktop-nav-border: #e2e8f0;
  --desktop-nav-ink: #64748b;
  --desktop-nav-hover-bg: #e6edf7;
  --desktop-nav-hover-ink: #245da8;
  --desktop-nav-active-bg: #fff;
  --desktop-nav-active-ink: #1d5fbd;
  --desktop-nav-active-border: #dce5f2;
  --desktop-nav-tooltip-bg: #172033;
  --desktop-nav-tooltip-ink: #f8fafc;
  display: flex;
  width: 64px;
  min-height: 0;
  flex: none;
  flex-direction: column;
  padding: 10px 7px 12px;
  border-right: 1px solid var(--desktop-nav-border);
  color: var(--desktop-nav-ink);
  background: var(--desktop-nav-bg);
}

.desktop-primary-nav__items {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.desktop-primary-nav__item {
  position: relative;
  display: flex;
  width: 50px;
  min-height: 48px;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border: 0;
  border-radius: 12px;
  color: inherit;
  background: transparent;
  cursor: pointer;
  transition: background-color 160ms ease, color 160ms ease, box-shadow 160ms ease;
}

.desktop-primary-nav__item:hover {
  color: var(--desktop-nav-hover-ink);
  background: var(--desktop-nav-hover-bg);
}

.desktop-primary-nav__item.active {
  color: var(--desktop-nav-active-ink);
  background: var(--desktop-nav-active-bg);
  box-shadow: 0 1px 3px rgba(15, 23, 42, .08), inset 0 0 0 1px var(--desktop-nav-active-border);
}

.desktop-primary-nav__item:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 1px;
}

.desktop-primary-nav__icon {
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
}

.desktop-primary-nav__icon svg {
  width: 21px;
  height: 21px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.desktop-primary-nav__item::after {
  position: absolute;
  z-index: 60;
  top: 50%;
  left: calc(100% + 10px);
  padding: 6px 9px;
  border-radius: 7px;
  color: var(--desktop-nav-tooltip-ink);
  background: var(--desktop-nav-tooltip-bg);
  box-shadow: 0 6px 18px rgba(15, 23, 42, .18);
  content: attr(data-tooltip);
  font-size: 12px;
  font-weight: 600;
  line-height: 1.2;
  opacity: 0;
  pointer-events: none;
  transform: translate(2px, -50%);
  transition: opacity 140ms ease, transform 140ms ease;
  white-space: nowrap;
}

.desktop-primary-nav__item:hover::after,
.desktop-primary-nav__item:focus-visible::after {
  opacity: 1;
  transform: translate(0, -50%);
}

.desktop-primary-nav__badge {
  position: absolute;
  top: 3px;
  right: 3px;
  display: grid;
  min-width: 15px;
  height: 15px;
  place-items: center;
  padding: 0 2px;
  border: 2px solid #f3f6fa;
  border-radius: 999px;
  color: #fff;
  background: #ef4444;
  font-size: 8px;
  font-weight: 800;
  line-height: 11px;
}

:global(html.platform-desktop.theme-dark) .desktop-primary-nav {
  --desktop-nav-bg: #0b1422;
  --desktop-nav-border: #28374d;
  --desktop-nav-ink: #91a3ba;
  --desktop-nav-hover-bg: #17263b;
  --desktop-nav-hover-ink: #b9d6ff;
  --desktop-nav-active-bg: #1b2b42;
  --desktop-nav-active-ink: #b9d6ff;
  --desktop-nav-active-border: #3a5575;
  --desktop-nav-tooltip-bg: #e2e8f0;
  --desktop-nav-tooltip-ink: #0f172a;
}

:global(html.platform-desktop.theme-dark) .desktop-primary-nav__badge {
  border-color: #0b1422;
}

@media (prefers-reduced-motion: reduce) {
  .desktop-primary-nav__item,
  .desktop-primary-nav__item::after { transition: none; }
}
</style>
