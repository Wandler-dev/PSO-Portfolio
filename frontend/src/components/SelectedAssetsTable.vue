<template>
  <section class="chart-panel">
    <div class="chart-title">入选策略</div>
    <el-empty v-if="!selectedAssets.length" description="当前没有权重 >= 1% 的入选策略" />
    <el-table v-else :data="selectedAssets" height="320" size="small">
      <el-table-column prop="asset_id" label="asset_id" />
      <el-table-column label="weight">
        <template #default="{ row }">{{ (row.weight * 100).toFixed(2) }}%</template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup>
defineProps({
  selectedAssets: { type: Array, default: () => [] }
})
</script>
