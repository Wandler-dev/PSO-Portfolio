<template>
  <div class="app-shell">
    <header class="dashboard-header">
      <div>
        <p class="eyebrow">粒子群优化可视化系统</p>
        <h1>PSO 智能投资组合优化系统</h1>
      </div>
      <div class="status-strip">
        <el-tag :type="backendStatusType" effect="dark">{{ backendStatusText }}</el-tag>
        <span>数据集：{{ displayDataSource }}</span>
        <span>候选策略数量：{{ dataSummary?.asset_count ?? '-' }}</span>
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
            <strong>数据集：{{ displayDataSource }}</strong>
          </div>
          <p>{{ localizedDataNote }}</p>
        </section>

        <KpiCards :result="optimizationResult" />

        <section class="chart-grid">
          <ConvergenceChart :curve="optimizationResult?.convergence_curve || []" />
          <AllocationChart :asset-weight-table="optimizationResult?.asset_weight_table || []" />
          <RiskReturnChart
            :points="optimizationResult?.risk_return_points || []"
            :best-point="optimizationResult?.best_point || null"
          />
        </section>

        <section class="selection-summary-grid">
          <SelectedAssetsTable :selected-assets="optimizationResult?.selected_assets || []" />
          <section class="chart-panel selection-note-card">
            <div class="chart-title">当前组合说明</div>
            <ul>
              <li>入选策略指权重 ≥ 1% 的候选策略。</li>
              <li>最优权重向量经过非负化和归一化处理，权重总和为 100%。</li>
              <li>Strategy_x 表示 UCI 数据集中的候选策略 ID。</li>
            </ul>
          </section>
        </section>

        <section class="comparison-section">
          <div class="comparison-heading">
            <div>
              <span class="section-label">预设参数对比</span>
              <h2>预设对比与组合变化</h2>
              <p>对比保守型、均衡型、激进型三组 PSO 参数下的风险、收益、夏普比率（Sharpe Ratio）与组合权重变化。</p>
            </div>
            <el-button type="primary" :loading="comparisonLoading" @click="loadPresetComparison">
              加载预设对比
            </el-button>
          </div>
          <el-alert
            v-if="comparisonError"
            type="error"
            :closable="false"
            show-icon
            :title="comparisonError"
          />
          <PresetComparisonChart :results="presetComparisonResults" :loading="comparisonLoading" />
          <PresetWeightComparisonChart :results="presetComparisonResults" :loading="comparisonLoading" />
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchDataSummary, fetchHealth, fetchPresets, optimizePreset, runOptimize } from './api/portfolio'
import ParameterPanel from './components/ParameterPanel.vue'
import KpiCards from './components/KpiCards.vue'
import ConvergenceChart from './components/ConvergenceChart.vue'
import AllocationChart from './components/AllocationChart.vue'
import RiskReturnChart from './components/RiskReturnChart.vue'
import SelectedAssetsTable from './components/SelectedAssetsTable.vue'
import PresetComparisonChart from './components/PresetComparisonChart.vue'
import PresetWeightComparisonChart from './components/PresetWeightComparisonChart.vue'

const backendStatus = ref('unknown')
const dataSummary = ref(null)
const presets = ref([])
const selectedPresetName = ref('balanced')
const optimizationResult = ref(null)
const presetComparisonResults = ref({})
const loading = ref(false)
const comparisonLoading = ref(false)
const errorMessage = ref('')
const comparisonError = ref('')

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

const displayDataSource = computed(() => {
  const source = dataSummary.value?.data_source
  if (source === 'uci') return 'UCI'
  if (source === 'simulated_fallback') return '模拟数据 fallback'
  return source || '-'
})

const localizedDataNote = computed(() => {
  if (!dataSummary.value) return '等待后端数据摘要。'
  if (dataSummary.value.data_source === 'uci') {
    return 'UCI Stock Portfolio Performance 数据集不是原始 date / symbol / close 股票价格序列。本系统将每个 ID 解释为一个候选选股权重策略，PSO 在这些候选策略之间优化资金分配权重。期望收益率来自 all period 表中的 original Annual Return，协方差矩阵由 1st / 2nd / 3rd / 4th period 的 Annual Return observations 构造。Annual Return 已是绩效指标，因此不再进行 252 个交易日年化。'
  }
  if (dataSummary.value.data_source === 'simulated_fallback') {
    return '当前使用模拟数据 fallback。该数据仅用于本地运行兜底，不代表真实 UCI 实验结果。'
  }
  return '已连接后端数据源，等待数据说明。'
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

async function loadPresetComparison() {
  comparisonLoading.value = true
  comparisonError.value = ''
  try {
    const presetNames = ['conservative', 'balanced', 'aggressive']
    const entries = await Promise.all(
      presetNames.map(async (presetName) => [presetName, await optimizePreset(presetName)])
    )
    presetComparisonResults.value = Object.fromEntries(entries)
    backendStatus.value = 'connected'
  } catch (error) {
    comparisonError.value = error.message || '预设对比请求失败'
  } finally {
    comparisonLoading.value = false
  }
}

onMounted(initializeDashboard)
</script>
