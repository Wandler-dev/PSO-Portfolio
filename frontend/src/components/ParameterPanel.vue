<template>
  <aside class="parameter-panel">
    <div class="panel-heading">
      <span class="section-label">参数控制</span>
      <h2>PSO 参数</h2>
    </div>

    <div class="preset-row">
      <el-button
        v-for="preset in presets"
        :key="preset.preset_name"
        :type="selectedPresetName === preset.preset_name ? 'primary' : 'default'"
        @click="selectPreset(preset)"
      >
        {{ presetLabel(preset.preset_name) }}
      </el-button>
    </div>

    <el-form label-position="top" class="parameter-form">
      <el-form-item label="粒子数量">
        <el-input-number v-model="localParams.particles" :min="20" :max="300" @change="markCustom" />
      </el-form-item>
      <el-form-item label="迭代次数">
        <el-input-number v-model="localParams.iterations" :min="50" :max="500" @change="markCustom" />
      </el-form-item>
      <el-form-item label="惯性权重">
        <el-slider v-model="localParams.inertia_weight" :min="0.1" :max="1.5" :step="0.1" @change="markCustom" />
      </el-form-item>
      <el-form-item label="个体学习因子 c1">
        <el-slider v-model="localParams.c1" :min="0.5" :max="3" :step="0.1" @change="markCustom" />
      </el-form-item>
      <el-form-item label="群体学习因子 c2">
        <el-slider v-model="localParams.c2" :min="0.5" :max="3" :step="0.1" @change="markCustom" />
      </el-form-item>
      <el-form-item label="无风险利率">
        <el-input-number v-model="localParams.risk_free_rate" :step="0.001" :precision="3" @change="markCustom" />
      </el-form-item>
      <el-form-item label="随机种子">
        <el-input-number v-model="localParams.random_seed" :min="0" :step="1" @change="markCustom" />
      </el-form-item>
      <el-form-item label="随机组合样本数">
        <el-input-number
          v-model="localParams.monte_carlo_samples"
          :min="2000"
          :step="500"
          @change="markCustom"
        />
      </el-form-item>
    </el-form>

    <el-button class="run-button" type="primary" :loading="loading" @click="$emit('optimize')">
      开始优化
    </el-button>
  </aside>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  params: { type: Object, required: true },
  presets: { type: Array, default: () => [] },
  selectedPresetName: { type: String, default: 'custom' },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['update:params', 'update:selectedPresetName', 'optimize'])
const localParams = reactive({ ...props.params })
const presetLabels = {
  conservative: '保守型',
  balanced: '均衡型',
  aggressive: '激进型',
  custom: '自定义参数'
}

watch(
  () => props.params,
  (nextParams) => Object.assign(localParams, nextParams),
  { deep: true }
)

watch(
  localParams,
  () => emit('update:params', { ...localParams }),
  { deep: true }
)

function selectPreset(preset) {
  Object.assign(localParams, {
    particles: preset.particles,
    iterations: preset.iterations,
    inertia_weight: preset.inertia_weight,
    c1: preset.c1,
    c2: preset.c2,
    risk_free_rate: preset.risk_free_rate,
    random_seed: preset.random_seed,
    monte_carlo_samples: preset.monte_carlo_samples
  })
  emit('update:selectedPresetName', preset.preset_name)
}

function markCustom() {
  emit('update:selectedPresetName', 'custom')
}

function presetLabel(name) {
  return presetLabels[name] || name
}
</script>
