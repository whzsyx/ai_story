"""项目应用信号"""

import uuid

from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_migrate


def create_mock_providers():
    """创建 Mock API 提供商配置。"""
    ModelProvider = apps.get_model('models', 'ModelProvider')

    mock_llm, created = ModelProvider.objects.get_or_create(
        name='Mock LLM API',
        defaults={
            'id': uuid.uuid4(),
            'provider_type': 'llm',
            'executor_class': 'core.ai_client.mock_llm_client.MockLLMClient',
            'api_url': 'http://localhost:8010/api/mock/llm/',
            'api_key': 'mock-api-key-not-required',
            'model_name': 'mock-llm-v1',
            'max_tokens': 4096,
            'temperature': 0.7,
            'top_p': 1.0,
            'timeout': 30,
            'is_active': True,
            'priority': 100,
            'rate_limit_rpm': 1000,
            'rate_limit_rpd': 100000,
            'extra_config': {
                'description': 'Mock LLM API，用于测试文案改写、分镜生成、运镜生成',
                'is_mock': True,
            }
        }
    )
    if created:
        print(f"✓ 已创建 Mock LLM 提供商: {mock_llm.name}")

    mock_text2image, created = ModelProvider.objects.get_or_create(
        name='Mock Text2Image API',
        defaults={
            'id': uuid.uuid4(),
            'provider_type': 'text2image',
            'executor_class': 'core.ai_client.mock_text2image_client.MockText2ImageClient',
            'api_url': 'http://localhost:8010/api/mock',
            'api_key': 'mock-api-key-not-required',
            'model_name': 'mock-text2image-v1',
            'timeout': 60,
            'is_active': True,
            'priority': 100,
            'rate_limit_rpm': 500,
            'rate_limit_rpd': 50000,
            'extra_config': {
                'description': 'Mock 文生图 API，返回占位图片用于测试',
                'is_mock': True,
                'default_ratio': '1:1',
                'default_resolution': '2k',
            }
        }
    )
    if created:
        print(f"✓ 已创建 Mock 文生图提供商: {mock_text2image.name}")

    mock_image2video, created = ModelProvider.objects.get_or_create(
        name='Mock Image2Video API',
        defaults={
            'id': uuid.uuid4(),
            'provider_type': 'image2video',
            'executor_class': 'core.ai_client.mock_image2video_client.MockImage2VideoClient',
            'api_url': 'http://localhost:8010/api/mock',
            'api_key': 'mock-api-key-not-required',
            'model_name': 'mock-image2video-v1',
            'timeout': 120,
            'is_active': True,
            'priority': 100,
            'rate_limit_rpm': 100,
            'rate_limit_rpd': 10000,
            'extra_config': {
                'description': 'Mock 图生视频 API，返回示例视频用于测试',
                'is_mock': True,
                'default_duration': 3.0,
                'default_fps': 24,
            }
        }
    )
    if created:
        print(f"✓ 已创建 Mock 图生视频提供商: {mock_image2video.name}")


def _ensure_default_prompt_template_set():
    """确保存在默认提示词集及其基础模板。"""
    User = apps.get_model('auth', 'User')
    PromptTemplateSet = apps.get_model('prompts', 'PromptTemplateSet')
    PromptTemplate = apps.get_model('prompts', 'PromptTemplate')

    system_user, _ = User.objects.get_or_create(
        username='system',
        defaults={
            'email': 'system@example.com',
            'is_staff': True,
            'is_superuser': False,
        }
    )

    stage_types = [
        'storyboard',
        'image_generation',
        'camera_movement',
        'video_generation',
    ]

    with transaction.atomic():
        template_set, _ = PromptTemplateSet.objects.get_or_create(
            name='默认提示词模板集',
            defaults={
                'description': '系统初始化生成的默认提示词模板集',
                'is_active': True,
                'is_default': True,
                'created_by': system_user,
            }
        )

        updated_fields = []
        if not template_set.is_active:
            template_set.is_active = True
            updated_fields.append('is_active')
        if not template_set.is_default:
            template_set.is_default = True
            updated_fields.append('is_default')
        if updated_fields:
            template_set.save(update_fields=updated_fields)

        for stage_type in stage_types:
            PromptTemplate.objects.get_or_create(
                template_set=template_set,
                stage_type=stage_type,
                defaults={
                    'template_content': '',
                    'variables': {},
                    'version': 1,
                    'is_active': True,
                }
            )


def run_post_migrate_initialization(sender, **kwargs):
    """在 migrate 执行完成后触发初始化逻辑。"""
    # if sender.label == 'models':
    create_mock_providers()

    # if sender.label == 'prompts':
    _ensure_default_prompt_template_set()


def _connect_post_migrate_signal():
    post_migrate.connect(
        run_post_migrate_initialization,
        dispatch_uid='apps.projects.post_migrate_initialization',
    )


_connect_post_migrate_signal()
