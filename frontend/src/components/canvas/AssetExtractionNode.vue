<template>
  <div
    class="asset-extraction-node"
    :class="`status-${effectiveStatus}`"
    :style="nodeStyle"
    @dblclick="handleNodeDoubleClick"
  >
    <div class="node-top">
      <div class="card-top">
        <div class="card-title-wrap">
          <span class="card-title">资产抽取</span>
          <span class="card-subtitle">{{ sourceTypeText }}</span>
        </div>
        <button
          class="pill-action"
          :disabled="isExecuting || status === 'processing'"
          @click.stop="handleExecute"
        >
          <span
            v-if="isExecuting"
            class="loading loading-spinner loading-xs"
          />
          <span v-else>执行抽取</span>
        </button>
      </div>

      <div class="card-meta">
        <span class="meta-chip">{{ itemCount }} 项待处理</span>
        <span
          v-if="selectedItem"
          class="meta-chip accent"
        >当前查看 {{ selectedItem.label || selectedItem.key }}</span>
      </div>
    </div>

    <div
      class="card-body prevent-canvas-wheel"
      @wheel.stop
      @mousedown.stop
    >
      <div
        v-if="data && data.summary"
        class="summary-box"
      >
        {{ data.summary }}
      </div>

      <div
        v-if="localItems.length"
        class="workspace-shell"
      >
        <div class="asset-grid-panel">
          <div class="asset-grid">
            <article
              v-for="item in localItems"
              :key="item.temp_id"
              class="asset-grid-card"
              :class="{
                active: selectedTempId === item.temp_id,
                matched: item.match_status === 'matched',
              }"
              role="button"
              tabindex="0"
              @click.stop="selectItem(item.temp_id)"
              @keyup.enter="selectItem(item.temp_id)"
            >
              <div class="card-top">
                <div>
                  <div class="asset-card-title">
                    {{ item.label || item.key }}
                  </div>
                  <div class="asset-card-key">
                    {{ item.key }}
                  </div>
                </div>
                <span class="item-confidence">{{ confidenceText(item.confidence) }}</span>
              </div>

              <div class="card-meta compact">
                <span class="item-group">{{ item.group || '未分组' }}</span>
                <span class="type-chip">{{ typeText(item.variable_type) }}</span>
              </div>

              <div class="asset-card-value">
                {{ shortValue(item.value) }}
              </div>

              <div class="card-footer compact">
                <span class="status-chip">{{ item.selected_asset_id ? '已关联' : '待处理' }}</span>
                <span class="ghost-link">点击查看</span>
              </div>
            </article>
          </div>
        </div>

        <div
          v-if="selectedItem"
          class="detail-panel"
        >
          <div class="detail-card">
            <div class="card-top">
              <div>
                <div class="detail-title">
                  {{ selectedItem.label || '未命名资产' }}
                </div>
                <div class="detail-subtitle">
                  点击保存后写回抽取结果
                </div>
              </div>
              <button
                class="pill-action ghost"
                :disabled="isSavingItem"
                @click.stop="handleSaveSelected"
              >
                <span
                  v-if="isSavingItem"
                  class="loading loading-spinner loading-xs"
                />
                <span v-else>保存当前项</span>
              </button>
            </div>

            <div class="detail-form">
              <label class="field-block">
                <span class="field-label">资产键</span>
                <input
                  v-model="selectedItem.key"
                  class="input input-bordered input-sm"
                  type="text"
                >
              </label>

              <label class="field-block">
                <span class="field-label">显示名称</span>
                <input
                  v-model="selectedItem.label"
                  class="input input-bordered input-sm"
                  type="text"
                >
              </label>

              <div class="field-row">
                <label class="field-block">
                  <span class="field-label">分组</span>
                  <input
                    v-model="selectedItem.group"
                    class="input input-bordered input-sm"
                    type="text"
                  >
                </label>
                <div class="field-block type-block">
                  <span class="field-label">资产类型</span>
                  <div class="type-summary-row">
                    <span class="type-pill">图片资产</span>
                    <button
                      class="ghost-link-btn"
                      type="button"
                      @click.stop="toggleAdvancedType"
                    >
                      {{ showAdvancedType ? '收起高级设置' : '高级设置' }}
                    </button>
                  </div>
                  <span class="field-hint">默认按图片资产处理，文本内容将作为文生图提示信息使用</span>
                </div>
              </div>

              <label
                v-if="showAdvancedType"
                class="field-block"
              >
                <span class="field-label">高级类型切换</span>
                <select
                  v-model="selectedItem.variable_type"
                  class="select select-bordered select-sm"
                >
                  <option value="image">图片</option>
                  <option value="string">字符串</option>
                  <option value="number">数字</option>
                  <option value="boolean">布尔值</option>
                  <option value="json">JSON</option>
                </select>
              </label>

              <label class="field-block">
                <span class="field-label">资产值</span>
                <textarea
                  v-model="editableValue"
                  class="textarea textarea-bordered value-textarea"
                  @change="handleValueChange"
                />
              </label>

              <label class="field-block">
                <span class="field-label">说明</span>
                <textarea
                  v-model="selectedItem.description"
                  class="textarea textarea-bordered textarea-sm detail-textarea"
                />
              </label>
            </div>
          </div>

          <div class="detail-card">
            <div class="card-top">
              <div>
                <div class="detail-title">
                  关联资产
                </div>
                <div class="detail-subtitle">
                  可绑定已有资产，或作为待应用动作
                </div>
              </div>
            </div>

            <div class="detail-form">
              <div class="field-row">
                <label class="field-block">
                  <span class="field-label">动作</span>
                  <select
                    v-model="selectedItem.selected_action"
                    class="select select-bordered select-sm"
                  >
                    <option value="">请选择动作</option>
                    <option value="bind_existing">关联已有</option>
                    <option value="create_new">生成新资产</option>
                    <option value="overwrite_existing">覆盖已有</option>
                    <option value="skip">跳过</option>
                  </select>
                </label>
                <label class="field-block">
                  <span class="field-label">已有关联</span>
                  <select
                    v-model="selectedItem.selected_asset_id"
                    class="select select-bordered select-sm"
                    :disabled="!requiresAssetSelection(selectedItem.selected_action)"
                  >
                    <option value="">请选择资产</option>
                    <option
                      v-for="asset in resolveAssetOptions(selectedItem)"
                      :key="asset.id || asset.asset_id"
                      :value="asset.id || asset.asset_id"
                    >
                      {{ (asset.key || '未命名') + (asset.group ? ` · ${asset.group}` : '') }}
                    </option>
                  </select>
                </label>
              </div>
            </div>
          </div>

          <div class="detail-card">
            <div class="card-top">
              <div>
                <div class="detail-title">
                  文生图
                </div>
                <div class="detail-subtitle">
                  先生成预览，满意后再保存为图片资产
                </div>
              </div>
              <button
                class="pill-action"
                :disabled="isGeneratingImage"
                @click.stop="handleGenerateImage"
              >
                <span
                  v-if="isGeneratingImage"
                  class="loading loading-spinner loading-xs"
                />
                <span v-else>生成预览</span>
              </button>
            </div>

            <div class="detail-form">
              <label class="field-block">
                <span class="field-label">生成提示词</span>
                <textarea
                  v-model="selectedItem.generation_prompt"
                  class="textarea textarea-bordered prompt-textarea"
                  placeholder="请输入用于文生图的提示词"
                />
              </label>

              <div
                v-if="previewImageUrl"
                class="preview-card"
              >
                <img
                  :src="previewImageUrl"
                  alt="预览图"
                  class="preview-image"
                >
                <div class="card-meta compact preview-meta">
                  <span class="meta-chip">预览完成</span>
                  <span
                    v-if="selectedItem.generated_image_preview && selectedItem.generated_image_preview.provider && selectedItem.generated_image_preview.provider.name"
                    class="meta-chip"
                  >
                    {{ selectedItem.generated_image_preview.provider.name }}
                  </span>
                </div>
                <button
                  class="pill-action secondary"
                  :disabled="isConfirmingImage"
                  @click.stop="handleConfirmImage"
                >
                  <span
                    v-if="isConfirmingImage"
                    class="loading loading-spinner loading-xs"
                  />
                  <span v-else>满意，保存为图片资产并绑定</span>
                </button>
              </div>
              <div
                v-else
                class="empty-inline"
              >
                生成完成后会在这里显示预览图
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else
        class="empty-state"
      >
        <div class="empty-title">
          暂未抽取到资产
        </div>
        <div class="empty-desc">
          执行后会解析文案并给出可关联、可编辑、可文生图的资产项
        </div>
      </div>
    </div>

    <div class="card-footer">
      <button
        class="pill-action secondary"
        :disabled="isApplying || !canApply"
        @click.stop="handleApply"
      >
        <span
          v-if="isApplying"
          class="loading loading-spinner loading-xs"
        />
        <span v-else>应用全部选择</span>
      </button>
    </div>
  </div>
</template>

<script>
import projectsAPI from '@/api/projects';

export default {
  name: 'AssetExtractionNode',
  props: {
    status: {
      type: String,
      default: 'pending'
    },
    position: {
      type: Object,
      default: () => ({ x: 0, y: 0 })
    },
    data: {
      type: Object,
      default: null
    },
    projectId: {
      type: [String, Number],
      required: true
    },
    availableAssets: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      isExecuting: false,
      isApplying: false,
      isSavingItem: false,
      isGeneratingImage: false,
      isConfirmingImage: false,
      localItems: [],
      selectedTempId: '',
      editableValue: '',
      showAdvancedType: false,
    };
  },
  computed: {
    nodeStyle() {
      return {
        position: 'absolute',
        left: `${this.position.x}px`,
        top: `${this.position.y}px`,
      };
    },
    effectiveStatus() {
      if (this.isExecuting || this.isApplying || this.isSavingItem || this.isGeneratingImage || this.isConfirmingImage) {
        return 'processing';
      }
      return this.status;
    },
    sourceTypeText() {
      const map = {
        rewritten_text: '来源：精修剧本',
        original_text: '来源：原始文案',
        original_topic: '来源：原始文案',
      };
      return map[(this.data && this.data.source_type)] || '来源：原始文案';
    },
    itemCount() {
      return this.localItems.length;
    },
    canApply() {
      return this.localItems.some(item => item.selected_action);
    },
    selectedItem() {
      return this.localItems.find(item => item.temp_id === this.selectedTempId) || null;
    },
    previewImageUrl() {
      return (this.selectedItem && this.selectedItem.generated_image_preview && this.selectedItem.generated_image_preview.url) || '';
    },
  },
  watch: {
    'data.items': {
      immediate: true,
      deep: true,
      handler(value) {
        this.localItems = (value || []).map(item => this.normalizeItem(item));
        if (!this.localItems.length) {
          this.selectedTempId = '';
          this.editableValue = '';
          return;
        }
        if (!this.localItems.some(item => item.temp_id === this.selectedTempId)) {
          this.selectedTempId = this.localItems[0].temp_id;
        }
        this.syncEditableValue();
      }
    },
    selectedTempId() {
      this.showAdvancedType = false;
      this.syncEditableValue();
    },
    selectedItem: {
      deep: true,
      handler() {
        this.syncEditableValue();
      }
    }
  },
  methods: {
    handleNodeDoubleClick(event) {
      if (!(event.target instanceof Element)) {
        this.$emit('node-dblclick');
        return;
      }

      if (event.target.closest('button, input, textarea, select, option, video, [contenteditable="true"], .prevent-canvas-wheel')) {
        return;
      }

      this.$emit('node-dblclick');
    },
    confidenceText(value) {
      const number = Number(value || 0);
      return `置信度 ${Math.round(number * 100)}%`;
    },
    typeText(value) {
      const map = {
        string: '字符串',
        number: '数字',
        boolean: '布尔值',
        json: 'JSON',
        image: '图片',
      };
      return map[value] || '未定义';
    },
    formatValue(value) {
      if (value == null) {
        return '暂无值';
      }
      if (typeof value === 'string') {
        return value;
      }
      try {
        return JSON.stringify(value, null, 2);
      } catch (error) {
        return String(value);
      }
    },
    shortValue(value) {
      const text = this.formatValue(value);
      return text.length > 88 ? `${text.slice(0, 88)}...` : text;
    },
    normalizeItem(item) {
      return {
        ...item,
        variable_type: item && item.variable_type ? item.variable_type : 'image',
      };
    },
    toggleAdvancedType() {
      this.showAdvancedType = !this.showAdvancedType;
    },
    parseEditableValue(raw, variableType) {
      if (variableType === 'json') {
        return raw ? JSON.parse(raw) : {};
      }
      if (variableType === 'number') {
        return raw === '' ? '' : Number(raw);
      }
      if (variableType === 'boolean') {
        return ['true', '1', 'yes', 'on'].includes(String(raw).toLowerCase());
      }
      return raw;
    },
    syncEditableValue() {
      if (!this.selectedItem) {
        this.editableValue = '';
        return;
      }
      const nextValue = this.formatValue(this.selectedItem.value);
      if (nextValue !== this.editableValue) {
        this.editableValue = nextValue;
      }
    },
    handleValueChange() {
      if (!this.selectedItem) {
        return;
      }
      try {
        this.selectedItem.value = this.parseEditableValue(this.editableValue, this.selectedItem.variable_type);
      } catch (error) {
        this.$message?.error('资产值格式不正确，请检查后再保存');
      }
    },
    selectItem(tempId) {
      this.selectedTempId = tempId;
    },
    requiresAssetSelection(action) {
      return action === 'bind_existing' || action === 'overwrite_existing';
    },
    resolveAssetOptions(item) {
      const candidateMap = new Map();
      (item.candidates || []).forEach(candidate => {
        candidateMap.set(candidate.asset_id, {
          id: candidate.asset_id,
          key: candidate.key,
          group: candidate.group,
        });
      });
      this.availableAssets.forEach(asset => {
        candidateMap.set(asset.id, asset);
      });
      return Array.from(candidateMap.values());
    },
    handleExecute() {
      this.isExecuting = true;
      try {
        this.$emit('execute', { stageType: 'asset_extraction', inputData: {} });
      } finally {
        this.isExecuting = false;
      }
    },
    applyStagePayload(stage) {
      const items = (stage && stage.domain_data && stage.domain_data.items) || (stage && stage.output_data && stage.output_data.items) || [];
      this.localItems = items.map(item => this.normalizeItem(item));
      if (this.localItems.length && !this.localItems.some(item => item.temp_id === this.selectedTempId)) {
        this.selectedTempId = this.localItems[0].temp_id;
      }
      this.syncEditableValue();
    },
    async handleSaveSelected() {
      if (!this.selectedItem) {
        return;
      }
      this.handleValueChange();
      this.isSavingItem = true;
      try {
        const response = await projectsAPI.updateAssetExtractionItem(this.projectId, {
          temp_id: this.selectedItem.temp_id,
          key: this.selectedItem.key,
          label: this.selectedItem.label,
          group: this.selectedItem.group,
          variable_type: this.selectedItem.variable_type || 'image',
          value: this.selectedItem.value,
          description: this.selectedItem.description,
          generation_prompt: this.selectedItem.generation_prompt,
          selected_action: this.selectedItem.selected_action,
          selected_asset_id: this.selectedItem.selected_asset_id,
        });
        this.applyStagePayload(response.stage);
        this.$message?.success('当前抽取项已保存');
      } catch (error) {
        console.error('[AssetExtractionNode] 保存抽取项失败:', error);
        this.$message?.error(error.response?.data?.error || error.message || '保存失败');
      } finally {
        this.isSavingItem = false;
      }
    },
    async handleGenerateImage() {
      if (!this.selectedItem) {
        return;
      }
      const prompt = (this.selectedItem.generation_prompt || this.selectedItem.value || '').trim();
      if (!prompt) {
        this.$message?.warning('请先输入文生图提示词');
        return;
      }
      this.isGeneratingImage = true;
      try {
        const response = await projectsAPI.generateAssetExtractionImage(this.projectId, {
          temp_id: this.selectedItem.temp_id,
          prompt,
        });
        this.applyStagePayload(response.stage);
        this.$message?.success('图片预览已生成');
      } catch (error) {
        console.error('[AssetExtractionNode] 生成图片预览失败:', error);
        this.$message?.error(error.response?.data?.error || error.message || '生成预览失败');
      } finally {
        this.isGeneratingImage = false;
      }
    },
    async handleConfirmImage() {
      if (!(this.selectedItem && this.selectedItem.generated_image_preview && this.selectedItem.generated_image_preview.url)) {
        this.$message?.warning('请先生成预览图');
        return;
      }
      this.isConfirmingImage = true;
      try {
        const response = await projectsAPI.confirmAssetExtractionImage(this.projectId, {
          temp_id: this.selectedItem.temp_id,
          key: this.selectedItem.key,
          group: this.selectedItem.group,
          description: this.selectedItem.description,
          value: this.selectedItem.generation_prompt || this.selectedItem.value || '',
        });
        this.applyStagePayload(response.stage);
        this.$message?.success('图片资产已创建并绑定');
        this.$emit('asset-bindings-updated');
      } catch (error) {
        console.error('[AssetExtractionNode] 确认图片资产失败:', error);
        this.$message?.error(error.response?.data?.error || error.message || '创建图片资产失败');
      } finally {
        this.isConfirmingImage = false;
      }
    },
    buildApplyPayload(item) {
      const payload = {
        temp_id: item.temp_id,
        action: item.selected_action,
      };

      if (this.requiresAssetSelection(item.selected_action)) {
        payload.asset_id = item.selected_asset_id;
      }

      if (item.selected_action === 'create_new') {
        payload.asset = {
          key: item.key,
          group: item.group,
          variable_type: item.variable_type || 'image',
          value: item.value,
          description: item.description || `从资产抽取节点生成：${item.label || item.key}`,
        };
      }

      if (item.selected_action === 'overwrite_existing') {
        payload.asset = {
          key: item.key,
          group: item.group,
          variable_type: item.variable_type || 'image',
          value: item.value,
          description: item.description || `从资产抽取节点更新：${item.label || item.key}`,
        };
      }

      return payload;
    },
    async handleApply() {
      const payload = this.localItems
        .filter(item => item.selected_action)
        .map(item => this.buildApplyPayload(item));

      if (!payload.length) {
        this.$message?.warning('请先选择要应用的资产项');
        return;
      }

      this.isApplying = true;
      try {
        const response = await projectsAPI.applyAssetExtraction(this.projectId, payload);
        this.applyStagePayload(response.stage);
        this.$message?.success('资产已更新并绑定到项目');
        this.$emit('asset-bindings-updated');
      } catch (error) {
        console.error('[AssetExtractionNode] 应用资产失败:', error);
        this.$message?.error(error.response?.data?.error || error.message || '应用资产失败');
      } finally {
        this.isApplying = false;
      }
    },
  }
};
</script>

<style scoped>
.asset-extraction-node {
  width: 980px;
  height: 620px;
  max-height: 620px;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.asset-extraction-node:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 52px rgba(15, 23, 42, 0.14);
  border-color: rgba(14, 165, 233, 0.18);
}

.layout-shell.theme-dark .asset-extraction-node {
  background: rgba(15, 23, 42, 0.94);
  border-color: rgba(148, 163, 184, 0.2);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.4);
}

.layout-shell.theme-dark .asset-extraction-node:hover {
  border-color: rgba(56, 189, 248, 0.22);
}

.node-top,
.card-footer {
  padding: 16px 18px;
}

.card-top,
.card-meta,
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.card-title,
.empty-title,
.detail-title,
.asset-card-title {
  font-weight: 700;
  color: #0f172a;
}

.card-subtitle,
.empty-desc,
.item-confidence,
.summary-box,
.detail-subtitle,
.asset-card-key,
.asset-card-value,
.ghost-link,
.empty-inline {
  color: #64748b;
}

.layout-shell.theme-dark .card-title,
.layout-shell.theme-dark .empty-title,
.layout-shell.theme-dark .detail-title,
.layout-shell.theme-dark .asset-card-title {
  color: #e2e8f0;
}

.layout-shell.theme-dark .card-subtitle,
.layout-shell.theme-dark .empty-desc,
.layout-shell.theme-dark .item-confidence,
.layout-shell.theme-dark .summary-box,
.layout-shell.theme-dark .detail-subtitle,
.layout-shell.theme-dark .asset-card-key,
.layout-shell.theme-dark .asset-card-value,
.layout-shell.theme-dark .ghost-link,
.layout-shell.theme-dark .empty-inline {
  color: #94a3b8;
}

.pill-action {
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(255, 255, 255, 0.96);
  color: #0f172a;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.25s ease;
}

.pill-action:hover:not(:disabled) {
  border-color: rgba(34, 211, 238, 0.5);
  box-shadow: 0 10px 24px rgba(56, 189, 248, 0.18);
  transform: translateY(-1px);
}

.pill-action.secondary {
  width: 100%;
}

.pill-action.ghost {
  background: rgba(248, 250, 252, 0.88);
}

.pill-action:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.layout-shell.theme-dark .pill-action {
  background: rgba(30, 41, 59, 0.92);
  color: #e2e8f0;
}

.card-meta {
  justify-content: flex-start;
  padding-top: 0;
  flex-wrap: wrap;
}

.card-meta.compact,
.card-footer.compact {
  padding: 0;
}

.meta-chip,
.item-group,
.type-chip,
.status-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 4px 10px;
  background: rgba(148, 163, 184, 0.12);
  font-size: 12px;
}

.meta-chip.accent,
.asset-grid-card.active .status-chip {
  background: rgba(34, 211, 238, 0.14);
  color: #0891b2;
}

.card-body {
  flex: 1;
  min-height: 0;
  padding: 0 18px 18px;
  overflow: auto;
}

.summary-box,
.empty-state,
.detail-card,
.asset-grid-card,
.preview-card {
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(248, 250, 252, 0.76);
}

.layout-shell.theme-dark .summary-box,
.layout-shell.theme-dark .empty-state,
.layout-shell.theme-dark .detail-card,
.layout-shell.theme-dark .asset-grid-card,
.layout-shell.theme-dark .preview-card {
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(148, 163, 184, 0.18);
}

.summary-box,
.empty-state {
  padding: 14px 16px;
  margin-bottom: 14px;
}

.workspace-shell {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.92fr);
  gap: 16px;
  min-height: 0;
}

.asset-grid-panel,
.detail-panel {
  min-height: 0;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}

.asset-grid-card {
  padding: 14px;
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.asset-grid-card:hover,
.asset-grid-card.active {
  transform: translateY(-4px);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.12);
  border-color: rgba(34, 211, 238, 0.32);
}

.asset-grid-card.matched {
  position: relative;
}

.asset-grid-card.matched::before,
.detail-card::before {
  content: '';
  display: block;
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(34, 211, 238, 0.88), rgba(59, 130, 246, 0.82));
  margin-bottom: 12px;
}

.asset-card-title {
  font-size: 15px;
  line-height: 1.3;
}

.asset-card-key {
  margin-top: 4px;
  font-size: 12px;
}

.asset-card-value {
  margin: 12px 0;
  min-height: 54px;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-card {
  padding: 14px 16px 16px;
}

.detail-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.field-hint {
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}

.type-block {
  justify-content: flex-start;
}

.type-summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.type-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 6px 12px;
  background: rgba(34, 211, 238, 0.12);
  color: #0891b2;
  font-size: 12px;
  font-weight: 600;
}

.ghost-link-btn {
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.ghost-link-btn:hover {
  color: #0891b2;
}

.layout-shell.theme-dark .field-label {
  color: #cbd5e1;
}

.layout-shell.theme-dark .field-hint,
.layout-shell.theme-dark .ghost-link-btn {
  color: #94a3b8;
}

.layout-shell.theme-dark .type-pill {
  background: rgba(34, 211, 238, 0.16);
  color: #67e8f9;
}

.value-textarea,
.detail-textarea,
.prompt-textarea {
  width: 100%;
  min-height: 88px;
}

.preview-card {
  padding: 12px;
}

.preview-image {
  width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
}

.preview-meta {
  margin: 10px 0 12px;
}

.empty-inline {
  border: 1px dashed rgba(148, 163, 184, 0.32);
  border-radius: 14px;
  padding: 18px 14px;
  text-align: center;
  font-size: 13px;
}

.empty-state {
  text-align: center;
}

.status-processing {
  border-color: rgba(56, 189, 248, 0.45);
}

.status-completed {
  border-color: rgba(148, 163, 184, 0.22);
}

.status-failed {
  border-color: rgba(248, 113, 113, 0.42);
}

@media (max-width: 1280px) {
  .asset-extraction-node {
    width: 920px;
  }
}
</style>
