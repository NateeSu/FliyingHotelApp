<template>
  <MainLayout v-if="authStore.isAuthenticated" />
  <router-view v-else />
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import MainLayout from '@/components/MainLayout_Material.vue'

const authStore = useAuthStore()
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

:root {
  --color-navy: #3338A0;
  --color-navy-dark: #1f2260;
  --color-navy-light: #2a2d80;
  --color-gold: #C59560;
  --color-yellow: #FCC61D;
  --color-white: #F7F7F7;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Prompt', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #F7F7F7;
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* Global button styles */
.n-button.n-button--primary-type {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%) !important;
  border: none !important;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(51, 56, 160, 0.3);
  transition: all 0.3s ease;
  color: #FCC61D !important;
}

.n-button.n-button--primary-type .n-button__content {
  color: #FCC61D !important;
}

.n-button.n-button--primary-type:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(51, 56, 160, 0.4);
}

.n-button.n-button--warning-type {
  background: linear-gradient(135deg, #FCC61D 0%, #C59560 100%) !important;
  border: none !important;
  color: #1f2260 !important;
  font-weight: 600;
}

.n-button.n-button--warning-type .n-button__content {
  color: #1f2260 !important;
}

.n-button.n-button--error-type .n-button__content {
  color: #F7F7F7 !important;
}

.n-button.n-button--success-type {
  background: linear-gradient(135deg, #C59560 0%, #b07f4d 100%) !important;
  color: #F7F7F7 !important;
  font-weight: 600;
}

.n-button.n-button--success-type .n-button__content {
  color: #F7F7F7 !important;
}

/* Text in buttons should always be visible */
.n-button {
  font-weight: 600;
}

.n-button--primary-type:not(:disabled) {
  color: #FCC61D !important;
}

.n-button--default-type .n-button__content {
  color: #3338A0 !important;
}

/* Form styles */
.n-input {
  font-weight: 500;
}

.n-input__input {
  color: #3338A0 !important;
}

.n-input__input::placeholder {
  color: #999 !important;
}

.n-select .n-base-selection-label {
  color: #3338A0 !important;
}

.n-select .n-base-selection-placeholder {
  color: #999 !important;
}

/* Alert styles */
.n-alert {
  font-weight: 500;
}

.n-alert.n-alert--success-type {
  background: rgba(197, 149, 96, 0.1) !important;
  border: 1px solid #C59560;
}

.n-alert.n-alert--success-type .n-alert__content {
  color: #3338A0 !important;
}

.n-alert.n-alert--info-type .n-alert__content {
  color: #3338A0 !important;
}

.n-alert.n-alert--warning-type .n-alert__content {
  color: #1f2260 !important;
}

/* Modal and Dialog */
.n-modal .n-card {
  border: 2px solid #3338A0;
}

.n-dialog {
  border: 2px solid #3338A0;
}

.n-dialog__title {
  color: #3338A0 !important;
  font-weight: 700;
}

.n-dialog__content {
  color: #3338A0 !important;
}

.n-dialog__action .n-button--primary-type {
  color: #FCC61D !important;
}

/* Dropdown */
.n-dropdown-menu {
  background: #F7F7F7 !important;
  border: 2px solid #3338A0;
}

.n-dropdown-option {
  color: #3338A0 !important;
  font-weight: 500;
}

.n-dropdown-option:hover {
  background: rgba(51, 56, 160, 0.1) !important;
}

.n-dropdown-option--selected {
  background: rgba(51, 56, 160, 0.15) !important;
  color: #3338A0 !important;
  font-weight: 600;
}

/* Data Table */
.n-data-table-th {
  color: #FCC61D !important;
  font-weight: 700;
}

.n-data-table-td {
  color: #3338A0 !important;
}

/* Tabs */
.n-tabs .n-tabs-tab {
  color: #3338A0 !important;
}

.n-tabs .n-tabs-tab--active {
  color: #FCC61D !important;
  font-weight: 700;
}

/* Pagination */
.n-pagination .n-pagination-item--active {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%) !important;
  color: #FCC61D !important;
  font-weight: 600;
}

.n-pagination .n-pagination-item {
  color: #3338A0 !important;
}

/* Switch */
.n-switch--active {
  background: linear-gradient(135deg, #C59560 0%, #b07f4d 100%) !important;
}

/* Tag colors override for better visibility */
.n-tag.n-tag--error-type {
  background: rgba(211, 47, 47, 0.15) !important;
  color: #c62828 !important;
  font-weight: 600;
}

.n-tag.n-tag--info-type {
  background: rgba(51, 56, 160, 0.15) !important;
  color: #3338A0 !important;
  font-weight: 600;
}

.n-tag.n-tag--success-type {
  background: rgba(197, 149, 96, 0.15) !important;
  color: #8B5F3E !important;
  font-weight: 600;
}

.n-tag.n-tag--warning-type {
  background: rgba(252, 198, 29, 0.15) !important;
  color: #B88A15 !important;
  font-weight: 600;
}

/* Scrollbar styles */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: #F7F7F7;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #3338A0 0%, #C59560 100%);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #2a2d80 0%, #b07f4d 100%);
}
</style>
