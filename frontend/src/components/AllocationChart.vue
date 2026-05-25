<template>
  <section class="chart-panel">
    <div class="chart-title">最优组合权重 Top 10</div>
    <div v-if="!topWeights.length" class="empty-state">等待优化结果</div>
    <div ref="chartRef" class="chart-canvas" />
  </section>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  assetWeightTable: { type: Array, default: () => [] }
})

const chartRef = ref(null)
let chart = null
const chartTextColor = '#e5e7eb'
const chartLabelColor = '#dbeafe'
const axisLineColor = 'rgba(226, 232, 240, 0.65)'
const splitLineColor = 'rgba(148, 163, 184, 0.25)'
const tooltipStyle = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  borderColor: 'rgba(148, 163, 184, 0.35)',
  textStyle: { color: '#f8fafc' }
}

const topWeights = computed(() =>
  [...props.assetWeightTable]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 10)
)

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 56, right: 20, top: 30, bottom: 76 },
    tooltip: {
      ...tooltipStyle,
      formatter: (params) => `候选策略：${params.name}<br/>权重：${(params.value * 100).toFixed(2)}%`
    },
    xAxis: {
      type: 'category',
      name: '候选策略',
      data: topWeights.value.map((row) => row.asset_id),
      nameTextStyle: { color: chartTextColor },
      axisLabel: { rotate: 40, color: chartLabelColor },
      axisLine: { lineStyle: { color: axisLineColor } },
      axisTick: { lineStyle: { color: axisLineColor } }
    },
    yAxis: {
      type: 'value',
      name: '权重',
      nameTextStyle: { color: chartTextColor },
      axisLabel: { color: chartLabelColor, formatter: (value) => `${(value * 100).toFixed(0)}%` },
      axisLine: { lineStyle: { color: axisLineColor } },
      splitLine: { lineStyle: { color: splitLineColor } }
    },
    series: [
      {
        type: 'bar',
        data: topWeights.value.map((row) => row.weight),
        itemStyle: { color: '#4f8cff', borderRadius: [4, 4, 0, 0] }
      }
    ]
  })
}

function resizeChart() {
  chart?.resize()
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', resizeChart)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
})
watch(topWeights, renderChart, { deep: true })
</script>
