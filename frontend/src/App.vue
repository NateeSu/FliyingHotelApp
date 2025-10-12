<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="thLocale" :date-locale="thDateLocale">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <router-view />
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { NConfigProvider, NMessageProvider, NNotificationProvider, NDialogProvider } from 'naive-ui'
import { thTH, dateThTH } from 'naive-ui'

// Theme customization
const themeOverrides = {
  common: {
    primaryColor: '#1976D2',
    primaryColorHover: '#1565C0',
    primaryColorPressed: '#0D47A1',
  }
}

const thLocale = thTH
const thDateLocale = dateThTH
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Prompt', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>
