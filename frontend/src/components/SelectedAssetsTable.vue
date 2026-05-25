<template>
  <section class="chart-panel selected-assets-card">
    <div class="chart-title">入选策略</div>
    <el-empty v-if="!selectedAssets.length" description="当前没有权重 ≥ 1% 的入选策略" />
    <div v-else class="table-wrapper">
      <el-table class="selected-assets-table" :data="selectedAssets" size="small">
        <el-table-column prop="asset_id" label="候选策略" min-width="150" />
        <el-table-column label="权重" width="110" align="right">
          <template #default="{ row }">{{ (row.weight * 100).toFixed(2) }}%</template>
        </el-table-column>
      </el-table>
    </div>
  </section>
</template>

<script setup>
defineProps({
  selectedAssets: { type: Array, default: () => [] }
})
</script>
