from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.agent.services.builtin_models import BuiltinAgentModelRegistry
from apps.agent.services.gateway import AgentGateway
from apps.users.models import UserPreference


class BuiltinAgentModelRegistryTestCase(TestCase):
    @override_settings(AGENT_SHOW_FREE_MODELS='true')
    def test_list_models_returns_free_models_when_enabled(self):
        models = BuiltinAgentModelRegistry.list_models()

        self.assertTrue(models)
        self.assertIn('builtin:opencode/big-pickle', [item['id'] for item in models])

    @override_settings(AGENT_SHOW_FREE_MODELS='false')
    def test_list_models_returns_empty_when_disabled(self):
        self.assertEqual(BuiltinAgentModelRegistry.list_models(), [])


class AgentModelListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='agent-user', password='secret123')
        self.client.force_authenticate(self.user)

    @override_settings(AGENT_SHOW_FREE_MODELS='true')
    def test_get_models_includes_builtin_free_models(self):
        response = self.client.get('/api/v1/agent/models/')

        self.assertEqual(response.status_code, 200)
        model_ids = [item['id'] for item in response.data['results']]
        self.assertIn('builtin:opencode/big-pickle', model_ids)
        self.assertIn('builtin:opencode/minimax-m2.5-free', model_ids)

    @override_settings(AGENT_SHOW_FREE_MODELS='true')
    def test_post_accepts_builtin_model_selection(self):
        response = self.client.post(
            '/api/v1/agent/models/',
            {'selected_model_provider_id': 'builtin:opencode/qwen3.6-plus-free'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        preference = UserPreference.objects.get(user=self.user, key='assistant_model_provider_id')
        self.assertEqual(preference.value, 'builtin:opencode/qwen3.6-plus-free')

    @override_settings(AGENT_SHOW_FREE_MODELS='false')
    def test_post_rejects_builtin_model_selection_when_disabled(self):
        response = self.client.post(
            '/api/v1/agent/models/',
            {'selected_model_provider_id': 'builtin:opencode/qwen3.6-plus-free'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)


class AgentGatewayTestCase(TestCase):
    @override_settings(AGENT_SHOW_FREE_MODELS='true')
    def test_resolve_model_target_supports_builtin_model(self):
        gateway = AgentGateway()

        target = gateway._resolve_model_target('builtin:opencode/nemotron-3-super-free')

        self.assertEqual(target['provider_id'], 'opencode')
        self.assertEqual(target['model_id'], 'nemotron-3-super-free')
        self.assertEqual(target['variant'], '')
