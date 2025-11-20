"""
Serializers for Workflow models.
"""
from rest_framework import serializers
from .models import (
    Workflow, WorkflowVersion, WorkflowTemplate,
    WorkflowVariable, WorkflowTrigger
)


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowTemplate model."""

    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'thumbnail_url', 'tags', 'definition', 'is_public',
            'is_featured', 'use_count', 'created_by', 'created_by_email',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'use_count', 'created_at', 'updated_at', 'created_by'
        ]

    def validate_definition(self, value):
        """Validate workflow definition structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Definition must be a JSON object.')

        required_keys = ['nodes', 'edges']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f'Definition must contain "{key}" key.')

        return value


class WorkflowTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template lists."""

    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'thumbnail_url', 'tags', 'is_featured', 'use_count',
            'created_at'
        ]
        read_only_fields = fields


class WorkflowVariableSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowVariable model."""

    class Meta:
        model = WorkflowVariable
        fields = [
            'id', 'workflow', 'name', 'variable_type', 'scope',
            'default_value', 'is_required', 'is_secret', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Validate variable data."""
        variable_type = attrs.get('variable_type')
        default_value = attrs.get('default_value')

        if default_value is not None and variable_type:
            # Validate default value matches type
            if variable_type == 'string' and not isinstance(default_value, str):
                raise serializers.ValidationError(
                    'Default value must be a string for string type variables.'
                )
            elif variable_type == 'number' and not isinstance(default_value, (int, float)):
                raise serializers.ValidationError(
                    'Default value must be a number for number type variables.'
                )
            elif variable_type == 'boolean' and not isinstance(default_value, bool):
                raise serializers.ValidationError(
                    'Default value must be a boolean for boolean type variables.'
                )
            elif variable_type == 'array' and not isinstance(default_value, list):
                raise serializers.ValidationError(
                    'Default value must be an array for array type variables.'
                )
            elif variable_type == 'object' and not isinstance(default_value, dict):
                raise serializers.ValidationError(
                    'Default value must be an object for object type variables.'
                )

        return attrs


class WorkflowTriggerSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowTrigger model."""

    class Meta:
        model = WorkflowTrigger
        fields = [
            'id', 'workflow', 'name', 'trigger_type', 'config',
            'cron_expression', 'timezone', 'webhook_url', 'webhook_secret',
            'is_active', 'execution_count', 'last_triggered_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'execution_count', 'last_triggered_at',
            'created_at', 'updated_at', 'webhook_url'
        ]

    def validate(self, attrs):
        """Validate trigger configuration."""
        trigger_type = attrs.get('trigger_type')

        if trigger_type == 'scheduled':
            cron_expression = attrs.get('cron_expression')
            if not cron_expression:
                raise serializers.ValidationError(
                    'Cron expression is required for scheduled triggers.'
                )

        return attrs

    def create(self, validated_data):
        """Create trigger and generate webhook URL if needed."""
        if validated_data.get('trigger_type') == 'webhook':
            import secrets
            workflow = validated_data['workflow']
            validated_data['webhook_url'] = (
                f'/api/v1/webhooks/workflows/{workflow.id}/'
                f'{secrets.token_urlsafe(32)}'
            )
            validated_data['webhook_secret'] = secrets.token_urlsafe(32)

        return super().create(validated_data)


class WorkflowVersionSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowVersion model."""

    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = WorkflowVersion
        fields = [
            'id', 'workflow', 'version_number', 'definition',
            'change_summary', 'metadata', 'created_by', 'created_by_email',
            'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'version_number', 'created_at', 'created_by'
        ]


class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for Workflow model."""

    success_rate = serializers.ReadOnlyField()
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    updated_by_email = serializers.EmailField(source='updated_by.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    variables = WorkflowVariableSerializer(many=True, read_only=True)
    triggers = WorkflowTriggerSerializer(many=True, read_only=True)

    class Meta:
        model = Workflow
        fields = [
            'id', 'organization', 'organization_name', 'name', 'description',
            'definition', 'status', 'is_active', 'version', 'current_version',
            'template', 'template_name', 'created_by', 'created_by_email',
            'created_by_name', 'updated_by', 'updated_by_email', 'tags',
            'metadata', 'execution_count', 'success_count', 'failure_count',
            'success_rate', 'last_executed_at', 'variables', 'triggers',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'version', 'current_version', 'created_by', 'updated_by',
            'execution_count', 'success_count', 'failure_count',
            'last_executed_at', 'created_at', 'updated_at'
        ]

    def validate_definition(self, value):
        """Validate workflow definition structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Definition must be a JSON object.')

        required_keys = ['nodes', 'edges']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f'Definition must contain "{key}" key.')

        # Validate nodes structure
        nodes = value.get('nodes', [])
        if not isinstance(nodes, list):
            raise serializers.ValidationError('Nodes must be an array.')

        for node in nodes:
            if not isinstance(node, dict):
                raise serializers.ValidationError('Each node must be an object.')

            node_required_keys = ['id', 'type']
            for key in node_required_keys:
                if key not in node:
                    raise serializers.ValidationError(
                        f'Each node must contain "{key}" key.'
                    )

        # Validate edges structure
        edges = value.get('edges', [])
        if not isinstance(edges, list):
            raise serializers.ValidationError('Edges must be an array.')

        for edge in edges:
            if not isinstance(edge, dict):
                raise serializers.ValidationError('Each edge must be an object.')

            edge_required_keys = ['id', 'source', 'target']
            for key in edge_required_keys:
                if key not in edge:
                    raise serializers.ValidationError(
                        f'Each edge must contain "{key}" key.'
                    )

        return value

    def create(self, validated_data):
        """Create workflow and set created_by."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user

        # Increment template use count if template is used
        if validated_data.get('template'):
            validated_data['template'].increment_use_count()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update workflow and set updated_by."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user

        return super().update(instance, validated_data)


class WorkflowListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for workflow lists."""

    success_rate = serializers.ReadOnlyField()
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Workflow
        fields = [
            'id', 'organization_name', 'name', 'status', 'is_active',
            'version', 'created_by_email', 'execution_count', 'success_rate',
            'last_executed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = fields


class WorkflowTestSerializer(serializers.Serializer):
    """Serializer for testing workflows with mock data."""

    input_data = serializers.JSONField(required=False, default=dict)
    dry_run = serializers.BooleanField(default=True)

    def validate_input_data(self, value):
        """Validate input data structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Input data must be a JSON object.')
        return value


class CreateVersionSerializer(serializers.Serializer):
    """Serializer for creating workflow versions."""

    definition = serializers.JSONField(required=False)
    change_summary = serializers.CharField(required=False, allow_blank=True)

    def validate_definition(self, value):
        """Validate workflow definition structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Definition must be a JSON object.')
        return value


class RollbackVersionSerializer(serializers.Serializer):
    """Serializer for rolling back to a version."""

    version_number = serializers.IntegerField(min_value=1, required=True)
