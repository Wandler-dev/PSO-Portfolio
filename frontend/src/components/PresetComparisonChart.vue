<template>
  <section class="chart-panel wide-panel comparison-panel">
    <div class="chart-title">Preset 风险-收益指标对比</div>
    <div v-if="loading" class="empty-state">正在加载预设对比</div>
    <div v-else-if="!hasResults" class="empty-state">点击“加载预设对比”查看三组参数结果</div>
    <div v-show="hasResults" class="metric-chart-grid">
      <div v-for="metric in metrics" :key="metric.key" class="metric-chart-card">
        <div class="metric-chart-title">{{ metric.label }}</div>
        <div :ref="(el) => setChartRef(metric.key, el)" class="metric-chart-canvas" />
      </div>
    </div>
  </section>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, nextTick, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  results: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false }
})

const presetOrder = ['conservative', 'balanced', 'aggressive']
const presetLabels = {
  conservative: '保守型',
  balanced: '均衡型',
  aggressive: '激进型'
}
const metrics = [
  { key: 'expected_return', label: '期望收益率（Expected Return）', color: '#28d6a3', percent: true },
  { key: 'volatility', label: '波动率（Volatility）', color: '#ffbf3f', percent: true },
  { key: 'sharpe_ratio', label: '夏普比率（Sharpe Ratio）', color: '#4f8cff', percent: false }
]

const chartRefs = {}
const charts = {}
const chartTextColor = '#e5e7eb'
const chartLabelColor = '#dbeafe'
const axisLineColor = 'rgba(226, 232, 240, 0.65)'
const splitLineColor = 'rgba(148, 163, 184, 0.25)'
const tooltipStyle = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  borderColor: 'rgba(148, 163, 184, 0.35)',
  textStyle: { color: '#f8fafc' }
}

const hasResults = computed(() => presetOrder.every((preset) => props.results?.[preset]))

function setChartRef(key, element) {
  if (element) {
    chartRefs[key] = element
    nextTick(() => renderMetric(key))
  }
}

function metricValues(metric) {
  return presetOrder.map((preset) => props.results?.[preset]?.[metric.key] ?? null)
}

function axisValue(metric, value) {
  if (!Number.isFinite(value)) return '-'
  return metric.percent ? `${(value * 100).toFixed(1)}%` : value.toFixed(2)
}

function tooltipValue(metric, value) {
  if (!Number.isFinite(value)) return '-'
  return metric.percent ? `${(value * 100).toFixed(2)}%` : value.toFixed(4)
}

function renderMetric(key) {
  const metric = metrics.find((item) => item.key === key)
  const element = chartRefs[key]
  if (!metric || !element || !hasResults.value) return
  if (!charts[key]) charts[key] = echarts.init(element)

  charts[key].setOption({
    grid: { left: 44, right: 18, top: 20, bottom: 42 },
    tooltip: {
      trigger: 'axis',
      ...tooltipStyle,
      formatter: (params) => {
        const point = params[0]
        return `${point.name}<br/>${metric.label}: ${tooltipValue(metric, point.value)}`
      }
    },
    xAxis: {
      type: 'category',
      data: presetOrder.map((preset) => presetLabels[preset]),
      axisLabel: { color: chartLabelColor },
      axisLine: { lineStyle: { color: axisLineColor } },
      axisTick: { lineStyle: { color: axisLineColor } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: chartLabelColor,
        formatter: (value) => axisValue(metric, value)
      },
      nameTextStyle: { color: chartTextColor },
      axisLine: { lineStyle: { color: axisLineColor } },
      splitLine: { lineStyle: { color: splitLineColor } }
    },
    series: [
      {
        type: 'bar',
        data: metricValues(metric),
        barWidth: 32,
        itemStyle: { color: metric.color, borderRadius: [4, 4, 0, 0] }
      }
    ]
  })
}

function renderAll() {
  nextTick(() => metrics.forEach((metric) => renderMetric(metric.key)))
}

function resizeCharts() {
  Object.values(charts).forEach((chart) => chart.resize())
}

watch(() => props.results, renderAll, { deep: true })
watch(() => props.loading, renderAll)

if (typeof window !== 'undefined') {
  window.addEventListener('resize', resizeCharts)
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  Object.values(charts).forEach((chart) => chart.dispose())
})
</script>
