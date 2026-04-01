import { generateLocalAssistantResponse } from '@/services/pageAgent/localAssistant';
import { pageAgentActionRegistry } from '@/services/pageAgent/actionRegistry';

const createMessage = (role, content, extra = {}) => ({
  id: `${role}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
  role,
  content,
  createdAt: Date.now(),
  suggestions: [],
  ...extra,
});

const createInitialAssistantMessage = (context) => createMessage(
  'assistant',
  context?.summary || '我已经准备好读取当前页面上下文。',
  { suggestions: [] }
);

const syncSession = (state) => {
  const scopeKey = state.activeScopeKey;
  if (!scopeKey) {
    return;
  }
  state.sessions = {
    ...state.sessions,
    [scopeKey]: {
      messages: [...state.messages],
    },
  };
};

const state = {
  visible: false,
  streaming: false,
  draft: '',
  currentContext: null,
  activeScopeKey: '',
  messages: [],
  sessions: {},
};

const getters = {
  visible: (state) => state.visible,
  streaming: (state) => state.streaming,
  draft: (state) => state.draft,
  currentContext: (state) => state.currentContext,
  messages: (state) => state.messages,
};

const mutations = {
  SET_VISIBLE(state, value) {
    state.visible = value;
  },
  SET_STREAMING(state, value) {
    state.streaming = value;
  },
  SET_DRAFT(state, value) {
    state.draft = value;
  },
  UPDATE_CONTEXT(state, context) {
    state.currentContext = context;
    state.activeScopeKey = context?.scopeKey || '';
  },
  SET_CONTEXT(state, context) {
    const nextScopeKey = context?.scopeKey || '';
    state.currentContext = context;
    state.activeScopeKey = nextScopeKey;

    const existingSession = nextScopeKey ? state.sessions[nextScopeKey] : null;
    if (existingSession?.messages?.length) {
      state.messages = [...existingSession.messages];
      return;
    }

    state.messages = context ? [createInitialAssistantMessage(context)] : [];
    syncSession(state);
  },
  ADD_MESSAGE(state, message) {
    state.messages = [...state.messages, message];
    syncSession(state);
  },
  REPLACE_LAST_MESSAGE(state, message) {
    if (!state.messages.length) {
      state.messages = [message];
    } else {
      state.messages = [...state.messages.slice(0, -1), message];
    }
    syncSession(state);
  },
};

const actions = {
  open({ commit }) {
    commit('SET_VISIBLE', true);
  },
  close({ commit }) {
    commit('SET_VISIBLE', false);
  },
  toggle({ commit, state }) {
    commit('SET_VISIBLE', !state.visible);
  },
  updateDraft({ commit }, value) {
    commit('SET_DRAFT', value);
  },
  registerContext({ commit, state }, context) {
    const scopeUnchanged = state.activeScopeKey === context?.scopeKey;
    const hadSession = Boolean(context?.scopeKey && state.sessions[context.scopeKey]);

    if (scopeUnchanged && hadSession) {
      commit('UPDATE_CONTEXT', context);
      return;
    }

    commit('SET_CONTEXT', context);
  },
  async sendMessage({ commit, state }, prompt) {
    const content = String(prompt || state.draft || '').trim();
    if (!content || state.streaming) {
      return;
    }

    commit('ADD_MESSAGE', createMessage('user', content));
    commit('SET_DRAFT', '');
    commit('SET_STREAMING', true);

    const pendingMessage = createMessage('assistant', '正在整理当前页面上下文...', {
      pending: true,
    });
    commit('ADD_MESSAGE', pendingMessage);

    try {
      await new Promise((resolve) => window.setTimeout(resolve, 280));
      const response = await generateLocalAssistantResponse({
        context: state.currentContext,
        prompt: content,
      });

      commit('REPLACE_LAST_MESSAGE', createMessage('assistant', response.content, {
        suggestions: response.suggestions || [],
      }));
    } catch (error) {
      commit('REPLACE_LAST_MESSAGE', createMessage('assistant', error.message || '页面助手处理失败，请稍后再试。'));
    } finally {
      commit('SET_STREAMING', false);
    }
  },
  async executeSuggestion({ commit, state }, suggestion) {
    if (!suggestion?.action || !state.currentContext?.scopeKey) {
      return;
    }

    try {
      const result = await pageAgentActionRegistry.execute(
        state.currentContext.scopeKey,
        suggestion.action,
        suggestion.params || {}
      );

      commit('ADD_MESSAGE', createMessage('assistant', result || `已执行「${suggestion.label || suggestion.action}」。`));
    } catch (error) {
      commit('ADD_MESSAGE', createMessage('assistant', error.message || '执行当前页面操作失败。'));
    }
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};
