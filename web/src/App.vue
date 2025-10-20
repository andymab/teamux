<template>
  <v-app>
    <v-main>
      <v-container class="py-8" max-width="900">
        <h1 class="text-h4 mb-6">teamux — AI SMM Tool</h1>

        <v-row class="mb-4" align="end">
          <v-col cols="12" md="8">
            <v-text-field v-model="url" label="URL статьи (HTML)" placeholder="https://..." />
          </v-col>
          <v-col cols="12" md="4">
            <v-btn :loading="loadingUrl" block color="primary" @click="analyzeFromUrl">Получить и
              проанализировать</v-btn>
          </v-col>
        </v-row>

        <v-textarea v-model="text" label="Текст для анализа" auto-grow rows="8" class="mb-4" />

        <v-row class="mb-4" align="center">
          <v-col cols="12" md="6">
            <v-select :items="models" v-model="model" label="Модель Groq" />
          </v-col>
          <v-col cols="12" md="6" class="d-flex gap-2">
            <v-btn :loading="loadingAnalyze" color="primary" @click="analyzeText">Анализировать
              текст</v-btn>
            <v-btn :loading="loadingPublish" color="success" @click="publishTG" :disabled="!analysis">Опубликовать в
              Telegram</v-btn>
          </v-col>
        </v-row>

        <v-card v-if="analysis" class="mb-6">
          <v-card-title>Результат анализа</v-card-title>
          <v-card-text>
            <pre style="white-space: pre-wrap">{{ analysis }}</pre>
          </v-card-text>
        </v-card>

        <v-divider class="my-6" />

        <v-row class="mb-4" align="end">
          <v-col cols="12" md="8">
            <v-text-field v-model="promptEn" label="Image prompt (EN)"
              placeholder="minimalist flat illustration of ..." />
          </v-col>
          <v-col cols="12" md="4">
            <v-btn :loading="loadingImage" block color="secondary" @click="generateImage">Сгенерировать и
              отправить картинку</v-btn>
          </v-col>
        </v-row>

        <v-alert v-if="error" type="error" variant="tonal">{{ error }}</v-alert>
        <v-alert v-if="ok" type="success" variant="tonal">Готово ✅</v-alert>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from './api'

const url = ref('')
const text = ref('')
const model = ref('llama-3.3-70b-versatile')
const models = ['llama-3.3-70b-versatile', 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768']

const analysis = ref('')
const promptEn = ref('')

const loadingUrl = ref(false)
const loadingAnalyze = ref(false)
const loadingPublish = ref(false)
const loadingImage = ref(false)

const error = ref('')
const ok = ref(false)

function handleErr(e: any) {
  error.value = e?.response?.data?.detail || e?.message || 'Ошибка'
  ok.value = false
}

async function analyzeFromUrl() {
  error.value = ''; ok.value = false; loadingUrl.value = true
  try {
    const { data } = await api.post('/analyze-url', { url: url.value, model: model.value })
    analysis.value = data.text
  } catch (e: any) { handleErr(e) } finally { loadingUrl.value = false }
}

async function analyzeText() {
  error.value = ''; ok.value = false; loadingAnalyze.value = true
  try {
    const { data } = await api.post('/analyze', { text: text.value, model: model.value })
    analysis.value = data.text
  } catch (e: any) { handleErr(e) } finally { loadingAnalyze.value = false }
}

async function publishTG() {
  error.value = ''; ok.value = false; loadingPublish.value = true
  try {
    await api.post('/publish', { text: analysis.value })
    ok.value = true
  } catch (e: any) { handleErr(e) } finally { loadingPublish.value = false }
}

async function generateImage() {
  error.value = ''; ok.value = false; loadingImage.value = true
  try {
    await api.post('/image', { prompt_en: promptEn.value })
    ok.value = true
  } catch (e: any) { handleErr(e) } finally { loadingImage.value = false }
}
</script>

<style>
html,
body,
#app {
  height: 100%;
}
</style>
