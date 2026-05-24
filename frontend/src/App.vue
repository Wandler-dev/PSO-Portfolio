<template>
  <div class="app-shell">
    <header class="dashboard-header">
      <div>
        <p class="eyebrow">Particle Swarm Optimization Dashboard</p>
        <h1>PSO 智能投资组合优化系统</h1>
      </div>
      <div class="status-strip">
        <el-tag :type="backendStatusType" effect="dark">{{ backendStatusText }}</el-tag>
        <span>数据源：{{ dataSummary?.data_source || '-' }}</span>
        <span>候选策略：{{ dataSummary?.asset_count ?? '-' }}</span>
      </div>
    </header>

    <el-alert
      v-if="errorMessage"
      class="top-alert"
      type="error"
      :closable="false"
      show-icon
      :title="errorMessage"
    />

    <main class="dashboard-grid">
      <ParameterPanel
        :params="params"
        :presets="presets"
        :selected-preset-name="selectedPresetName"
        :loading="loading"
        @update:params="updateParams"
        @update:selected-preset-name="selectedPresetName = $event"
        @optimize="handleOptimize"
      />

      <section class="main-content">
        <section class="data-band">
          <div>
            <span class="section-label">数据集</span>
            <strong>{{ dataSummary?.data_source || '未连接' }}</strong>
          </div>
          <p>{{ dataSummary?.source_notes || '等待后端数据摘要。' }}</p>
        </section>

        <KpiCards :result="optimizationResult" />

        <section class="chart-grid">
          <ConvergenceChart :curve="optimizationResult?.convergence_curve || []" />
          <AllocationChart :asset-weight-table="optimizationResult?.asset_weight_table || []" />
          <RiskReturnChart
            :points="optimizationResult?.risk_return_points || []"
            :best-point="optimizationResult?.best_point || null"
          />
          <SelectedAssetsTable :selected-assets="optimizationResult?.selected_assets || []" />
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchDataSummary, fetchHealth, fetchPresets, runOptimize } from './api/portfolio'
import ParameterPanel from './components/ParameterPanel.vue'
import KpiCards from './components/KpiCards.vue'
import ConvergenceChart from './components/ConvergenceChart.vue'
import AllocationChart from './components/AllocationChart.vue'
import RiskReturnChart from './components/RiskReturnChart.vue'
import SelectedAssetsTable from './components/SelectedAssetsTable.vue'

const backendStatus = ref('unknown')
const dataSummary = ref(null)
const presets = ref([])
const selectedPresetName = ref('balanced')
const optimizationResult = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const params = reactive({
  particles: 100,
  iterations: 200,
  inertia_weight: 0.7,
  c1: 1.5,
  c2: 1.5,
  risk_free_rate: 0.0,
  random_seed: 42,
  monte_carlo_samples: 3000
})

const backendStatusText = computed(() => {
  if (backendStatus.value === 'connected') return '已连接'
  if (backendStatus.value === 'failed') return '请求失败'
  return '未连接'
})

const backendStatusType = computed(() => {
  if (backendStatus.value === 'connected') return 'success'
  if (backendStatus.value === 'failed') return 'danger'
  return 'info'
})

function applyPreset(preset) {
  if (!preset) return
  Object.assign(params, {
    particles: preset.particles,
    iterations: preset.iterations,
    inertia_weight: preset.inertia_weight,
    c1: preset.c1,
    c2: preset.c2,
    risk_free_rate: preset.risk_free_rate,
    random_seed: preset.random_seed,
    monte_carlo_samples: preset.monte_carlo_samples
  })
  selectedPresetName.value = preset.preset_name
}

function updateParams(nextParams) {
  Object.assign(params, nextParams)
}

async function initializeDashboard() {
  errorMessage.value = ''
  try {
    await fetchHealth()
    backendStatus.value = 'connected'
    const [summary, presetList] = await Promise.all([fetchDataSummary(), fetchPresets()])
    dataSummary.value = summary
    presets.value = presetList
    applyPreset(presetList.find((preset) => preset.preset_name === 'balanced'))
  } catch (error) {
    backendStatus.value = 'failed'
    errorMessage.value = '后端服务未连接，请先启动 FastAPI 服务'
  }
}

async function handleOptimize() {
  loading.value = true
  errorMessage.value = ''
  try {
    const payload = {
      ...params,
      preset_name: selectedPresetName.value === 'custom' ? null : selectedPresetName.value
    }
    optimizationResult.value = await runOptimize(payload)
    backendStatus.value = 'connected'
  } catch (error) {
    backendStatus.value = 'failed'
    errorMessage.value = error.message || '优化请求失败'
  } finally {
    loading.value = false
  }
}

onMounted(initializeDashboard)
</script>
